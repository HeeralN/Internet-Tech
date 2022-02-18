'''
Implements load bearing. 
Uses select.select(inputs,outputs,)
'''

import sys
import socket
import select
import threading

def connectSocket():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()
    return ss

# INPUTS
# python rs.py rsListenPort ts1Hostname ts1ListenPort ts2Hostname ts2ListenPort
def rs(rsListenPort, ts1Hostname, ts1ListenPort, ts2Hostname, ts2ListenPort):
    
    # TODO check that all arguments have been passed in?
    # if(len(sys.argv) == 6):
    #     raise TypeError("Expected 6 inputs.")

    # open socket for RS
    rs_socket = connectSocket()
    #localhost_addr = socket.gethostbyname(socket.gethostname())
    rs_bind = ('', rsListenPort) # TODO update host or port?
    rs_socket.bind(rs_bind)
    rs_socket.listen(1)

    # connect to TS1
    ts1_socket = connectSocket()
    ts1_bind = (ts1Hostname, ts1ListenPort)  # TODO update host or port?
    ts1_socket.connect(ts1_bind)

    # connect to TS2
    ts2_socket = connectSocket()
    ts2_bind = (ts2Hostname, ts2ListenPort)  # TODO update host or port?
    ts2_socket.connect(ts2_bind)

    # Start accepting data from the client
    rsockid, addr = rs_socket.accept()
    rsockid.setblocking(0)
    # ts1sockid, addr1 = ts1_socket.accept()
    # ts2sockid, addr2 = ts2_socket.accept()

    inputs = [rsockid, ts1_socket, ts2_socket]
    ss = [rs_socket, ts1_socket, ts2_socket]

    message_buffer = {}
    # inputs = [rsockid, ts1sockid, ts2sockid]
    outputs = []

    while inputs:
        readable, writable, errors = select.select(inputs, outputs, [], 5)
        print(readable, writable, errors)

        if readable or writable:
            for r in readable:
                if r in ss:
                    conn, add = r.accept()
                    conn.setblocking(0)
                    inputs.append(conn)

                else:
                    data = r.recv(200)
                    print("Message from client:{}".format(data.decode('utf-8')))
                    outputs.append(r)
                    print(r)
                    message_buffer[r] = data
                    inputs.remove(r)

            for w in writable:
                msg = message_buffer[w]
                w.send(msg)
                outputs.remove(w)
        else:
            print("time out")
            rs_socket.close()
            inputs.remove(rs_socket)

    # Close the server socket
    rs_socket.close()


if __name__ == "__main__":
    #rs = threading.Thread(name='rs', target=rs)
    #rs.start()

    # rs.py rsListenPort ts1Hostname ts1ListenPort ts2Hostname ts2ListenPort

    rs(50007, '', 50008, '', 50009)  # TODO REMOVE LATER