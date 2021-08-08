import socket, sys, select, time
from os import listdir, getcwd, path
import threading
import re

from messageProtocol import decodeMessage, encodeMessageStdin, ERROR_MSG

##### NETWORK VARIABLES
HOST = ''
PORT = 5000

##### DATABASE VARIABLES
FILES = {} # Like a "cache" for the server, it maps all existing files in database and, for each one, stores the number of times each word searched by clients appears
DATABASE_PATH = path.join( path.abspath(getcwd()),  "database" ) # Database path

##### SERVER VARIABLES
REQUESTS_ENTRIES = [] # All entries in which the server will "pay attention" and accept requests. Default value is just stdin for reading adm commands
ACTIVE_CLIENTS = {} # All clients that are currently active/connected with the server
SERVER_IS_ALIVE = True # Defines server state
WORKERS = [] # All workers threads alive

##### DATABASE METHODS
def __getTextFile(filename):
    """
        Get text from filename.
        :param filename: file name with its extension
        :return If the file exist, returns True e the whole text, else returns False e empty string
    """
    try: # Try to read text from file
        f = open(path.join(DATABASE_PATH, filename), 'r')
        text = f.read()

        f.close()
        return True, text
    except(FileNotFoundError): # If file not found, return 
        return False, ""

def __mappingExistingFiles():
    """
        Maps all existing files in database folder.
    """
    database_files = [f for f in listdir(DATABASE_PATH) if path.isfile(path.join(DATABASE_PATH, f))] # Get the name of all files in database folder

    for f in database_files: # For each file in database, create a dict for it in cache
        if(f not in FILES.keys()):
            FILES[f] = {}

##### SEARCH METHODS
def __search(filename, word):
    """
        Search engine core.
        :param filename: file name with its extension
        :param word: the word to be searched
        :return The number of times da word appears in filename. If the file is not in database, returns -1.
    """
    word_finder = re.compile(r'\w+').findall # Create finder to search for the word

    existFile, text = __getTextFile(filename) # Get the whole text if file exists

    wrd = word.lower()

    if(existFile):
        if(not FILES[filename]): # If file is not in server's cache
            FILES[filename] = {}

        if(wrd in FILES[filename].keys()): # If word's counting were requested before
            return FILES[filename][wrd]
        else:
            count = len(list(filter(lambda w: w.lower() == wrd, word_finder(text)))) # Find word in text
            FILES[filename][wrd] = count # Save word's counting in server's cache

            return count

    else:
        return -1

def searchWordInFile(infos):
    """
        Search for the word in the specified file, looking in the FILES cache first. This search is not case sensitive.
        :param infos: dictionary with file name and the word to be searched.
        :return The search result encoded in the defined protocol.
    """
    filename = infos['file']['name']+ "." + infos['file']['ext'] # Get filename
    word = infos['word'] # Get word to be searched

    occr = __search(filename, word) # Call search engine core

    if(occr == -1): # Return message informing that the file doesn't exist in database
        return "result:existFile:False.result:occr:-1." + "result:file:name:" + infos['file']['name'] + ".result:file:ext:" + infos['file']['ext'] +".result:word:" + word + "."
    else: # Return message informing that the file exist in database and word's counting in the file
        return "result:existFile:True.result:occr:" + str(occr) + ".result:file:name:" + infos['file']['name'] + ".result:file:ext:" + infos['file']['ext'] +".result:word:" + word + "."

##### SERVER METHODS
def __initServer():
    """
        Create and initialize server.
        :return Server's socket
    """
    __mappingExistingFiles()

    socket_server = socket.socket()

    socket_server.bind((HOST, PORT))

    socket_server.listen(5)

    socket_server.setblocking(False)
    socket_server.settimeout(10.0) # Set a limit time to a thread to be waiting in any "blocking" function

    REQUESTS_ENTRIES.append(socket_server)

    return socket_server

def __initStdinWorker():
    """
        Create and start a worker to handle stdin commands from adm.
        :return Return adm's socket
    """
    socket_stdin = socket.socket()

    socket_stdin.connect(("localhost", PORT))

    worker_stdin = threading.Thread(target=__readStdin, args=(socket_stdin,))

    print("[MAIN] Created thread to read adm commands.")
    worker_stdin.start()

    return socket_stdin

def __readStdin(socket_stdin):
    """
        Read commands from stdin and sends to main to execute.
        :param socket_stdin: stdin worker's socket 
    """
    while True:
        if(not SERVER_IS_ALIVE): # If server is not alive anymore...
            print("[MAIN] Killing stdin thread...")
            socket_stdin.close() # Close stdin socket
            sys.exit() # Kill thread
        
        command = input() # Read a command from stdin

        cmd = encodeMessageStdin(command) # Encode command into a message

        socket_stdin.send(cmd.encode('utf-8')) # Send to server 

        time.sleep(1)

def __acceptConnection(socket_server):
    """
        Accept clients' connection requests
        :param socket_server: server's socket
        :return A server socket's "child" which will handle the new connection and the client's address.
    """

    new_socket, client_address = socket_server.accept() # Accept client's connection

    ACTIVE_CLIENTS[new_socket] = client_address 

    return new_socket, client_address

def __attendClient(conn_socket, client_address):
    """
        Attend client's requests
        :param conn_socket: server-client connection socket
        :param client_address: client's IP and port connected.
        :return The search result encoded in the defined protocol.
    """
    while True:
            search_msg = conn_socket.recv(1024) # Receive client's message

            conn_socket.send(search_msg) # Send the same message as a notification message

            infos = decodeMessage(search_msg.decode('utf-8')) # Decode message

            if(infos):
                if(infos['action'] == 'end'): # If client wants to end connection...
                    print("[" + threading.current_thread().getName() + "] " + str(client_address) + " >>> finished connection")
                    conn_socket.close()
                    break
                elif(infos['action'] == 'sch'): # If client wants to search a word in a file...
                    print("[" + threading.current_thread().getName() + "] " + str(client_address) + " >>> search started")
                    result_msg = searchWordInFile(infos) # Call the function to search for the word

                    conn_socket.send(result_msg.encode('utf-8')) # Send back the result
                    print("[" + threading.current_thread().getName() + "] " + str(client_address) + " >>> search finished and send")
            else: # If some error occured, 'infos' variable is empty
                print("[" + threading.current_thread().getName() + "] " + str(client_address) + " >>> error occurred")
                conn_socket.send(ERROR_MSG.encode('utf-8')) # Send back to client that an error occured

def __attendAdministrator(socket_server, socket_adm):
    """
        Attend adm's requests.\n
        Possible requests:
            - kill: to kill the server
            - count_workers: to count active threads
            - historical_clients: to show in terminal all clients address who connected with the server.\n
        :param socket_server: server-client connection socket
        :param socket_adm: server-server connection socket
    """
    msg = socket_adm.recv(1024) # Receive message from adm thread (stdin)
    command = decodeMessage(msg.decode('utf-8')) # Decode message

    if(command):
        cmd = command['cmd']

        if(cmd == 'kill'): # If adm wants to kill the server...
            global SERVER_IS_ALIVE
            SERVER_IS_ALIVE = False

            if(threading.active_count()-2 > 0): # If there is worker still working...
                print("[MAIN] There are workers attending clients. Waiting for workers to finish their tasks...")
                for worker in WORKERS: # Wait until all workers finish their tasks
                    worker.join()
            print("[MAIN]  Killing server...")
            socket_server.close()
            sys.exit()

        elif(cmd == 'count_workers'): 
            print("[MAIN] The number of active workers is: " + str(threading.active_count()-2)) # Print the number of active workers
        elif(cmd == 'historical_clients'):
            print("[MAIN] All the clients that connected with server at least one are: " + str(list(ACTIVE_CLIENTS.values()))) # Print all clients that connected with the server

def __getRequestApplicants():
    """
        Get sockets who request something.
        :return A list with all applicants.
    """
    to_read, to_write, err = select.select(REQUESTS_ENTRIES, [], [])

    return to_read

def __dispatchClientToWorker(conn_socket, client_addr):
    """
        Create worker and dispatch client's request to him.
        :param conn_socket: server-client connection socket
        :param client_addr: client's IP and port connected.
    """
    worker = threading.Thread(target=__attendClient, args=(conn_socket, client_addr))

    print("[MAIN] Client " + str(client_addr) + "dispatched to: " + str(worker.getName()))
    worker.start()

    WORKERS.append(worker)

def searchAppServer():
    """
        Search app main - Server side.
    """
    print("[MAIN] Starting server...")
    socket_server = __initServer() # Initialize server

    # Initialize and accept connection with 'stdin' thread and add the socket in possible entries to get requests
    socket_stdin = __initStdinWorker()
    conn_stdin_socket, stdin_adrss = __acceptConnection(socket_server)
    REQUESTS_ENTRIES.append(conn_stdin_socket)
    
    print("[MAIN] Server is alive!")
    while SERVER_IS_ALIVE:
        applicants = __getRequestApplicants() # Get who requested something

        for applicant in applicants:
            if applicant == socket_server: # If some client request something
                conn_socket, client_adrss = __acceptConnection(socket_server) # Accept client's connection
                print("[MAIN] " + str(client_adrss) + " >>> connected")

                __dispatchClientToWorker(conn_socket, client_adrss) # Dispatch request to a worker
            elif applicant == conn_stdin_socket: # If adm send a command 
                __attendAdministrator(socket_server, conn_stdin_socket) # Attend adm's request


if __name__ == "__main__":
    searchAppServer()
