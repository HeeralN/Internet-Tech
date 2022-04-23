import threading
import time
import random
import socket
import select
import argparse
import queue
from time import sleep
from functools import reduce

# Settings
# Retransmission timeout
RTO = 0.500
# Number of application bytes in one packet
CHUNK_SIZE = 8
# Initial sequence number for sender transmissions
INIT_SEQNO = 5
# dummy ACK number for sender's packets
__ACK_UNUSED = 2345367

# Message class: we use this class to structure our protocol
# message. The fields in our protocol are:
# seq no: the starting sequence number of application bytes
# on this packet
# ack no: the cumulative ACK number of application bytes
# being acknowledged in this ACK
# len: the number of application bytes being transmitted on
# this packet
# msg: the actual application payload on this packet
# The methods `serialize` and `deserialize` allow the
# conversion of a protocol object to bytes transmissible
# through a sendto() system call and the bytes from a
# recvfrom() system call into a protocol structure.
class Msg:
    def __init__(self, seq, ack, msg):
        self.seq = int(seq)
        self.ack = int(ack)
        self.msg = str(msg)
        self.len = len(self.msg)

    def serialize(self):
        ser_repr = (str(self.seq) + ' | ' + str(self.ack) + ' | ' +
                    str(self.len) + ' | ' + self.msg)
        return ser_repr.encode('utf-8')

    def __str__(self):
        repr  = "Seq: " + str(self.seq) + '   '
        repr += "ACK: " + str(self.ack) + '   '
        repr += "Len: " + str(self.len) + '   '
        repr += "Msg: " + self.msg.strip()
        return repr

    @staticmethod
    def deserialize(ser_bytes_msg):
        ser_msg = ser_bytes_msg.decode('utf-8')
        parts = ser_msg.split('|')
        if len(parts) >= 4:
            return Msg(int(parts[0]),
                       int(parts[1]),
                       '|'.join(parts[3:])[1:])
        else:
            print("Error in deserializing into Msg object.")
            exit(-1)

### Helper methods.
#### Initialize a UDP socket
def init_socket(receiver_binding):
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("[S]: Sender socket created")
    except socket.error as err:
        print('socket open error: {} \n'.format(err))
        exit()
    return cs

#### Slurp a file into a single string.
#### Warning: do not use on very large files
def get_filedata(filename):
    print ("[S] Transmitting file {}".format(filename))
    f = open(filename, 'r')
    filedata = f.read()
    f.close()
    return filedata

#### Chunk a large string into fixed size chunks.
#### The first chunk is a string with the number of
#### following chunks. 
#### `seq_to_msgindex` tracks the index of the packet
#### that will contain a given sequence number as its
#### starting sequence number.
def chunk_data(filedata):
    global CHUNK_SIZE
    global INIT_SEQNO
    messages = [filedata[i:i + CHUNK_SIZE]
                for i in range(0, len(filedata),
                               CHUNK_SIZE)]
    messages = [str(len(filedata))] + messages
    content_len = reduce(lambda x, y: x + len(y),
                         messages, 0)
    seq_to_msgindex = {}
    accumulated = INIT_SEQNO
    for i in range(0, len(messages)):
        seq_to_msgindex[accumulated] = i
        accumulated += len(messages[i])
    return messages, content_len, seq_to_msgindex

#### Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port',
                        type = int,
                        help = "receiver port to connect to (default 50007)",
                        default = 50007)
    parser.add_argument('--infile',
                        type = str,
                        help = "name of input file (default test-input.txt)",
                        default = "test-input.txt")
    parser.add_argument('--winsize',
                        type = int,
                        help = "Window size to use in pipelined reliability",
                        default = 20)
    args = parser.parse_args()
    return vars(args)

############################################
# Main reliable sending loop
def send_reliable(cs, filedata, receiver_binding, win_size):
    global RTO
    global INIT_SEQNO
    global __ACK_UNUSED
    messages, content_len, seq_to_msgindex = chunk_data(filedata)

    win_left_edge = INIT_SEQNO
    win_right_edge = min(win_left_edge + win_size,
                         INIT_SEQNO + content_len)

    # Method to transmit all data between window left and
    # right edges. Typically used for just fresh
    # transmissions (retransmissions use transmit_one()).
    def transmit_entire_window_from(left_edge):
        latest_tx = left_edge
        while latest_tx < win_right_edge:
            assert (latest_tx in seq_to_msgindex)
            index = seq_to_msgindex[latest_tx]
            msg = messages[index]
            if (latest_tx + len(msg) <=
                win_right_edge):
                m = Msg(latest_tx, __ACK_UNUSED, msg)
                cs.sendto(
                    m.serialize(),
                    receiver_binding)
                print ("Transmitted {}".format(str(m)))
                latest_tx += len(msg)
            else:
                break
        # return last seq no that was actually transmitted
        return latest_tx

    # Transmit one packet from the left edge of the
    # window. Used for retransmissions in pipelined
    # reliability, and also for fresh transmissions in
    # stop-and-wait reliability.
    def transmit_one():
        assert (win_left_edge in seq_to_msgindex)
        index = seq_to_msgindex[win_left_edge]
        msg = messages[index]
        m = Msg(win_left_edge, __ACK_UNUSED, msg)
        cs.sendto(m.serialize(), receiver_binding)
        print ("Transmitted {}".format(str(m)))
        return win_left_edge + len(msg)

    # TODO: This is where you will make your changes. You
    # will not need to change any other parts of this file.
    
    def buffering_transmit_window(first_to_tx):
        latest_tx = first_to_tx
        while latest_tx < win_right_edge:
            index = seq_to_msgindex[latest_tx]
            msg = messages[index]
            if (latest_tx + len(msg) <= win_right_edge):
                m = Msg(latest_tx, __ACK_UNUSED, msg)
                if m.seq not in buffer: 
                    buffer.append(m.seq)
                    print ("Buffered {}".format(str(m)))
                latest_tx += len(msg)
            else:
                break      
        
        latest_tx = transmit_entire_window_from(first_to_tx)
        print("latest_tx: ", latest_tx)
        #if latest_tx in seq_to_msgindex:
        first_to_tx = latest_tx #+ len(messages[seq_to_msgindex[latest_tx]])
        print("first_tx: ", first_to_tx)
        return first_to_tx
    

    inputs = [cs]
    outputs = []
    error = []

    buffer = []
    last_acked = -1  # tracks the highest ACKed number so far
    first_to_tx = INIT_SEQNO
    final_ack = INIT_SEQNO + content_len
    # print("final_ack: ",final_ack)
    
    # print("seq_to_msgindex: ",seq_to_msgindex)
    

    last_seq = lambda x: x - len(messages[seq_to_msgindex[x] - 1])
    i = 0
    while win_left_edge < final_ack:
        if i == 3: break
        i += 1
        # buffer.remove(-1)
        print("\nBuffer: ",buffer)
        readable, writable, exceptional = select.select(inputs, outputs, error, RTO)

        if readable: # Received ACK
            #while True:
            data, addr = cs.recvfrom(100)
            msg = Msg.deserialize(data)

            print("Received: ", str(msg))
            print(win_left_edge, win_right_edge)
            last_acked = msg.ack  # highest ACK received
            print("last_acked: ", last_acked)
            # Remove packets from buffer up to but not including last_acked
            for p in buffer:
                if p < last_acked:
                    buffer.remove(p)
            print("Updated: ", buffer)

            # Update window upon ack and transmit next packet. 
            # Don't slide past last_acked because it may be dropped packet
            if (win_left_edge <= last_acked):
                win_left_edge = msg.ack if msg.ack < final_ack else win_left_edge
                win_right_edge = min(win_left_edge + win_size, INIT_SEQNO + content_len)
                print("win_right_edge: ", win_right_edge)

                # Transmit 
                first_to_tx = buffering_transmit_window(first_to_tx)
                print("buffered: ", buffer)
                print("second first_to_tx: ",first_to_tx)
        else:
            print("hoahfawe")
            if buffer:
                print("awefa333333")
                # RTO occurred, retransmit last ack'd
                temp_left = win_left_edge
                win_left_edge = buffer[0]
                first_to_tx = transmit_one()
                
                win_left_edge = first_to_tx
            else:
                # Initial transmission 
                first_to_tx = buffering_transmit_window(first_to_tx)
                print("initial first_to_tx: ",first_to_tx)
                print("buffered: ", buffer)
                if first_to_tx >= final_ack:
                    break
    
    print("seq_to_msgindex: ",seq_to_msgindex)





if __name__ == "__main__":
    args = parse_args()
    filedata = get_filedata(args['infile'])
    receiver_binding = ('', args['port'])
    cs = init_socket(receiver_binding)
    send_reliable(cs, filedata, receiver_binding,
                  args['winsize'])
    cs.close()
    print("[S] Sender finished all transmissions.")
