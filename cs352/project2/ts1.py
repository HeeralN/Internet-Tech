import threading
import time
import random

import socket

def ts():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    server_binding = ('', 50008)
    ss.bind(server_binding)
    ss.listen(1)
    host = socket.gethostname()
    print("[S]: Server host name is {}".format(host))
    localhost_ip = (socket.gethostbyname(host))
    print("[S]: Server IP address is {}".format(localhost_ip))
    csockid, addr = ss.accept()
    print ("[S]: Got a connection request from a client at {}".format(addr))

    # Build lookup table
    table = dict()
    inputFile = open("PROJ2-DNSTS1.txt", 'r')
    inputlines = inputFile.read().lower().splitlines()

    for line in inputlines:
        splitLine = line.split()
        table[splitLine[0]] = splitLine[1] + " " + splitLine[2]

    # print(table)

    while True:
        # Recieve query
        query=csockid.recv(100).decode('utf-8')
        if query != u'':   # TODO update later
            print("ts1", query)
            # Resolve query and send back response (or not)
            try:
                response = table[query]
                csockid.send(response.encode('utf-8'))
            except KeyError:
                pass
            

if __name__ == "__main__":
    t1 = threading.Thread(name='ts1', target=ts)
    t1.start()