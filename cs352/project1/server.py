import threading
import time
import random

import socket

def server():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    server_binding = ('', 50007)
    ss.bind(server_binding)
    ss.listen(1)
    host = socket.gethostname()
    print("[S]: Server host name is {}".format(host))
    localhost_ip = (socket.gethostbyname(host))
    print("[S]: Server IP address is {}".format(localhost_ip))
    csockid, addr = ss.accept()
    print ("[S]: Got a connection request from a client at {}".format(addr))

    # send a intro message to the client.  
    msg = "Welcome to CS 352!"
    csockid.send(msg.encode('utf-8'))

    # STEP 4
    # Receive data from the client and send back the reverse message
    data_from_client=csockid.recv(100)
    rec_msg = data_from_client.decode('utf-8')
    # print("[C]: Data received from client: {}".format(rec_msg))
    csockid.send(rec_msg.encode('utf-8')[::-1])
    print("[S]: Step 4 - Sent reversed string to client")
    # FINISHED STEP 4
    
    # STEP 5
    outfile = open("out-proj.txt", 'w')
    count = 0
    length = int(csockid.recv(100).decode('utf-8'))
    # print("[C]: Data received from client: {}".format(length))

    while count < length:
        # time.sleep(random.random() * 1)
        data_from_client=csockid.recv(200)
        reverse_msg = data_from_client.decode('utf-8')[::-1]
        # print("[C]: Reversed data received from client: {}".format(reverse_msg))

        # send reversed string to out-proj.txt
        outfile.write(reverse_msg[1:] + "\n")
        count+=1
    outfile.close()
    print("[S]: Step 5 - Wrote data to output file \"out-proj.txt\"")
    # FINISHED STEP 5

    # Close the server socket
    ss.close()
    exit()



if __name__ == "__main__":
    t1 = threading.Thread(name='server', target=server)
    t1.start()
    print("Done.")