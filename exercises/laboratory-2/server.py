import socket, re, math
from os import listdir, getcwd, path
from messageProtocol import decodeMessage

HOST = ''
PORT = 5000
FILES = {}
DATABASE_PATH = path.join( path.abspath(getcwd()),  "database" )
ERROR_MSG = "result:error."
THRESHOLD = math.inf

def getTextFile(filename):

    if(filename not in FILES.keys()):
        return False, ""
    
    f = open(path.join(DATABASE_PATH, filename), 'r')
    text = f.read()

    f.close()

    return True, text

def search(filename, word):
    word_finder = re.compile(r'\w+').findall

    existFile, text = getTextFile(filename)

    if(existFile):

        wrd = word.lower()
        
        count = len(list(filter(lambda w: w.lower() == wrd, word_finder(text))))

        if not FILES[filename]:
            FILES[filename] = {}

        FILES[filename][wrd] = count

        return count

    else:
        return -1

def searchWordInFile(infos):
    filename = infos['file']['name']+ "." + infos['file']['ext']
    word = infos['word']

    occr = search(filename, word)

    if(occr == -1):
        return "result:existFile:False.result:occr:-1." + "result:file:name:" + infos['file']['name'] + ".result:file:ext:" + infos['file']['ext'] +".result:word:" + word + "."
    else:
        return "result:existFile:True.result:occr:" + str(occr) + ".result:file:name:" + infos['file']['name'] + ".result:file:ext:" + infos['file']['ext'] +".result:word:" + word + "."

def mappingExistingFiles():
    database_files = [f for f in listdir(DATABASE_PATH) if path.isfile(path.join(DATABASE_PATH, f))]

    for f in database_files:
        if(f not in FILES.keys()):
            FILES[f] = {}

def searchAppServer():
    number_clients = 0 

    mappingExistingFiles()

    socket_server = socket.socket()

    socket_server.bind((HOST, PORT))

    socket_server.listen(5)

    while True:
        new_socket_echo, address = socket_server.accept()

        while True:
            search_msg = new_socket_echo.recv(1024)

            new_socket_echo.send(search_msg)

            infos = decodeMessage(search_msg.decode('utf-8'))

            if(infos):
                if(infos['action'] == 'end'):
                    number_clients += 1
                    new_socket_echo.close()
                    break
                elif(infos['action'] == 'sch'):
                    result_msg = searchWordInFile(infos)

                    new_socket_echo.send(result_msg.encode('utf-8'))
            else:
                new_socket_echo.send(ERROR_MSG.encode('utf-8'))

        if(THRESHOLD == number_clients):
            break

    socket_server.close()

if __name__ == "__main__":
    searchAppServer()
