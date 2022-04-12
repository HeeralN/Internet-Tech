import sys
import socket

def ts1(portNum):
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[TS1]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    server_binding = ('', portNum)
    ss.bind(server_binding)
    ss.listen(1)
    host = socket.gethostname()
    print("[TS1]: Server host name is {}".format(host))

    localhost_ip = (socket.gethostbyname(host))
    print("[TS1]: Server IP address is {}".format(localhost_ip))
    
    csockid, addr = ss.accept()
    print ("[TS1]: Got a connection request from a client at {}".format(addr))

    # Build lookup table
    dns = dict()
    inputFile = open("PROJ2-DNSTS1.txt", 'r')
    inputlines = inputFile.read().splitlines()
    
    for line in inputlines:
        dns[line.split()[0].lower()] = line
    

    while True:
        data = csockid.recv(4096).decode("utf-8").strip()
        data_lower = data.lower()
        if not data:
            break
        print("[TS1]: Received Message: " + data)
		
        if data_lower in dns:
            print("[TS1]: Data found in DNS")
            ret = dns.get(data_lower) + " IN"
            csockid.send(ret.encode("utf-8"))
            
    csockid.close()
    ss.close()
    exit()


if __name__ == "__main__":
    # ts1(50008)
    ts1(int(sys.argv[1]))