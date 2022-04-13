import select
import socket

try:
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[S]: Server socket created")
except socket.error as err:
    print('socket open error: {}\n'.format(err))
    exit()
# ss.setblocking(0)
server_binding = ("", 50007)
ss.bind(server_binding)
ss.listen(2)

message_buffer = {}
inputs = [ss]
outputs = []
while inputs:
    print(inputs,outputs)
    readable, writable, errors = select.select(inputs, outputs, [], 20)

    if readable or writable:
        for r in readable:
            if r is ss:
                conn, add = r.accept()
                # conn.setblocking(0)
                inputs.append(conn)

            else:
                data = r.recv(200)
                print("Message from client:{}".format(data.decode('utf-8')))
                outputs.append(r)
                print(r)
                message_buffer[r] = "hello from server!".encode('utf-8')
                inputs.remove(r)

        for  w in writable:
            msg = message_buffer[w]
            w.send(msg)
            outputs.remove(w)
    else:
        print("time out")
        ss.close()
        inputs.remove(ss)