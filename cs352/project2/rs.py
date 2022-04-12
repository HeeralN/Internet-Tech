import sys
import socket
import select

def connectSocket():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[RS]: Server socket created")
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
    ts1_socket.settimeout(5)

    # connect to TS2
    ts2_socket = connectSocket()
    ts2_bind = (ts2Hostname, ts2ListenPort)  # TODO update host or port?
    ts2_socket.connect(ts2_bind)
    ts2_socket.settimeout(5)

    # Start accepting data from the client
    client_sockid, addr = rs_socket.accept()
    
    while True:
        data = client_sockid.recv(200).decode("utf-8")
        if not data:
            break
        
        print("\n[RS]: Data received from client: "+ data)

        # Send the data to both servers
        ts1_socket.send(data.encode("utf-8"))
        ts2_socket.send(data.encode("utf-8"))

        # Try receiving from both servers
        # Check if TS1 sent any response
        try:
            msg = ts1_socket.recv(200).decode("utf-8")
            print("[RS]: Data received from TS1: " + msg)
            client_sockid.send(msg.encode("utf-8"))

        except socket.timeout:
            
            try:
                msg = ts2_socket.recv(200).decode("utf-8")
                print("[RS]: Data received from TS2: " + msg)
                client_sockid.send(msg.encode("utf-8"))

            except socket.timeout:
                # send client msg: "DomainName - TIMED OUT"
                timedOut_msg = data + ' - TIMED OUT'
                client_sockid.send(timedOut_msg.encode("utf-8"))
                pass


    # Close the server socket
    rs_socket.close()
    ts1_socket.close()
    ts2_socket.close()
    exit()


if __name__ == "__main__":
    # rs.py rsListenPort ts1Hostname ts1ListenPort ts2Hostname ts2ListenPort
    rs(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))

    # python rs.py 50007 localhost 50008 localhost 50009