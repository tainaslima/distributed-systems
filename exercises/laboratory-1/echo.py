import socket

HOST = ''
PORT = 5000

socket_echo = socket.socket()

socket_echo.bind((HOST, PORT))

socket_echo.listen(5)

new_socket_echo, address = socket_echo.accept()

while True:
    message = new_socket_echo.recv(1024)

    if message:
        print("Got the message \""+ message.decode('utf-8') +"\" ! Echoing..")
        new_socket_echo.send(message)
        print("Echoed!")
    else:
        break

new_socket_echo.close()
socket_echo.close()