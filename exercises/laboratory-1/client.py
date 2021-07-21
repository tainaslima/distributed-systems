import socket

HOST = 'localhost'
PORT = 5000

socket_client = socket.socket()

socket_client.connect((HOST, PORT))

entry = str(input("Type what do you want to echo or type 'close' (without quotations) to close the app.\n"))
while(entry != "close"):
    socket_client.send(entry.encode('utf-8'))

    message = socket_client.recv(1024)
    print(message.decode('utf-8'))

    entry = str(input("Type what do you want to echo or type 'close' (without quotations) to close the app.\n"))

socket_client.close()