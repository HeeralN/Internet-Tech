'''
Implements load bearing. 
Uses select.select(inputs,outputs,)
'''

import sys
import socket
import select

def connectSocket():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()


# INPUTS
# python rs.py rsListenPort ts1Hostname ts1ListenPort ts2Hostname ts2ListenPort
def rs():
    
    # TODO check that all arguments have been passed in?

    # open socket for RS
    rs_socket = connectSocket()
    rs_socket.bind( ('', 50007) )  # TODO update host

    rs.setblocking(0) # timeout if response not received


    # connect to TS1
    ts1_socket = connectSocket()
    ts1_bind = ('', 50008)  # TODO update host
    ts1_socket.bind(ts1_bind)
    ts1_socket.connect(ts1_bind)

    # connect to TS2
    ts2_socket = connectSocket()
    ts2_bind = ('', 50009)  # TODO update host
    ts2_socket.bind()
    ts2_socket.connect(ts2_bind)

    rsockid, addr = rs_socket.accept()

    message_buffer = {}
    inputs = [rs_socket, ts1_socket, ts2_socket]
    outputs = []

    while True:
        readable, writable, errors = select.select(inputs, outputs, [], 5)

        if readable or writable:
            for r in readable:
                if r is rs_socket:
                    conn, add = r.accept()
                    conn.setblocking(0)
                
                else:
                    data = r.recv(200).decode("utf-8")
                    print("Message from client: {}".format(data))
                    outputs.append(r)
                    message_buffer[r] = "hello from server".encode("utf-8")
                    inputs.remove(r)

            for w in writable:
                msg = message_buffer[w]
                w.send(msg)
                outputs.remove(w)
                
        else:
            print("Server timed out")  # TODO add more things here, send message to client




if __name__ == "__main__":
    pass