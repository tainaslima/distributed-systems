import socket
from sys import int_info
from messageProtocol import encodeMessageCli, decodeMessage, interpretMessage

HOST = 'localhost'
PORT = 5000
           
def searchAppCli():

    socket_client = socket.socket()

    socket_client.connect((HOST, PORT))

    action = int(input("What do you want to do?\nChoose:\n0 - end app\n1- search for a word in a text file\n"))
    while(action == 1):
        filename, extension = input("Type the file in which word will be searched.\nE.g. mercado.txt\n").split(".")
    
        word = input("Type the word to be searched.\n")
        while(not word):
            print("Please, type a valid word.")
            word = input("Type the word to be searched.\n")

        search_msg = encodeMessageCli(action, filename, extension, word)

        socket_client.send(search_msg.encode('utf-8'))

        notify_msg = socket_client.recv(1024)
        
        print("\n")
        print(interpretMessage(decodeMessage(notify_msg.decode('utf-8')))) 

        result_msg = socket_client.recv(1024)

        pretty_answer = interpretMessage(decodeMessage(result_msg.decode('utf-8')))

        print(pretty_answer)

        action = int(input("What do you want to do?\nChoose:\n0 - end app\n1- search for a word in a text file\n"))

    print("Thanks for using our app. Bye!")

    end_msg = encodeMessageCli(action)

    socket_client.send(end_msg.encode('utf-8'))

    socket_client.close()

if __name__ == "__main__":
    searchAppCli()