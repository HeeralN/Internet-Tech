import socket
import sys
import time

def client(sHostname, sListenPort, id):
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket created")
    except socket.error as err:
        print('socket open error: {} \n'.format(err))
        exit()

    sListenPort = int(sListenPort)
    sHostname = socket.gethostbyname(sHostname)

    # connect to the server on local machine
    server_binding = (sHostname, sListenPort)
    cs.connect(server_binding)

    msg = "Hello! from client "+str(id)

    cs.send(msg.encode("utf-8"))

    data = cs.recv(200)
    print(data.decode('utf-8'))
    time.sleep(15)
    cs.close()
    exit()


if __name__ == "__main__":
    localhost = socket.gethostbyname(socket.gethostname())
    client(localhost, 50020, 1)
    print("done.")