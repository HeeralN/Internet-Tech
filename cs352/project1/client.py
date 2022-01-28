import threading
import time
import random

import socket

def client():
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket created")
    except socket.error as err:
        print('socket open error: {} \n'.format(err))
        exit()
        
    # Define the port on which you want to connect to the server
    port = 50007
    localhost_addr = socket.gethostbyname(socket.gethostname())

    # connect to the server on local machine
    server_binding = (localhost_addr, port)
    cs.connect(server_binding)

    # Receive data from the server
    data_from_server=cs.recv(200)
    print("[C]: Data received from server: {}".format(data_from_server.decode('utf-8')))

    # STEP 4
    # send a intro message to the client.  
    msg = "Welcome to CS 352!"
    cs.send(msg.encode('utf-8'))
    
    # Retrieve reversed message from server
    data_from_server=cs.recv(100)
    print("[C]: Data received from server: {}".format(data_from_server.decode('utf-8')))
    # FINISHED STEP 4

    # STEP 5
    filemsg = open('in-proj.txt','r')

    all_lines = []
    for line in filemsg.readlines():
        all_lines.append(line[:-1])
    
    length = str(len(all_lines))
    cs.send(length.encode('utf-8'))
    for curr_line in all_lines:
        time.sleep(random.random() * 1)
        cs.send(curr_line.encode('utf-8'))
    
    filemsg.close()
    print("[C]: Step 5 - Sent file data to server")
    # FINISHED STEP 5

    # close the client socket
    cs.close()
    exit()


if __name__ == "__main__":
    t2 = threading.Thread(name='client', target=client)
    t2.start()

    # time.sleep(5)
    print("Done.")