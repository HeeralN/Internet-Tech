import sys
import socket

def client(sHostname, sListenPort, id):
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
    server_binding = (sHostname, sListenPort) #TODO double check this
    cs.connect(server_binding)

    # read data from input file
    inputFile = open("PROJ2-HNS.txt", 'r')
    inputlines = inputFile.read().splitlines()
    
    # open write file
    outputFile = open("RESOLVED.txt", 'w+')

    # Send query to rs
    print(inputlines)
    for line in inputlines:
        cs.send(line.encode())
        data_from_server=cs.recv(200).decode('utf-8')
        print("[C]: Data received: {}".format(data_from_server))
        outputFile.write(data_from_server)
    '''
    # Recieve response from rs. Fill in dictionary
    for i in range(len(inputlines)):
        response = cs.recv(200).decode('utf-8')
        outputFile.write(response)
    '''
    # close files
    inputFile.close()
    outputFile.close()

    # close the client socket
    cs.close()
    exit()

if __name__ == "__main__":
    client('', 50007, 1)
    pass