##### GLOBAL MESSAGES 
ERROR_MSG = "result:error." # Error message returned to client when something wrong happens

def str2Bool(entry):
    return True if entry == "True" else False

def encodeMessageStdin(msg):
    return "action:stdin.cmd:"+msg+"."

def encodeMessageCli(action, *params):
    if(action == 0):
        return "action:end."
    elif(action == 1):

        fn = params[0]
        ext = params[1]
        wrd = params[2]

        return "action:sch.file:name:" + fn + ".file:ext:" + ext + ".word:"+ wrd + "."
    else:
        return -1

def decodeMessage(msg):
    list_msg = msg.split(".")
    list_msg.remove("")
    infos = {}

    if(list_msg):

        for entry in list_msg:
            list_entry = entry.split(":")
            
            if('' in list_entry):
                list_entry.remove('')

            if(len(list_entry) == 2):
                infos[list_entry[0]] = list_entry[1]
            elif(len(list_entry) == 3):
                if(list_entry[0] not in infos.keys()):
                    infos[list_entry[0]] = {}
                infos[list_entry[0]][list_entry[1]] = list_entry[2]
            else:
                if(list_entry[0] not in infos.keys()):
                    infos[list_entry[0]] = {}

                if(list_entry[1] not in infos[list_entry[0]].keys()):
                    infos[list_entry[0]][list_entry[1]] = {}
                infos[list_entry[0]][list_entry[1]][list_entry[2]] = list_entry[3]
    return infos

def interpretMessage(msg):
    if("result" in msg.keys()):
        if(msg['result'] == 'error'):
            return "There was an error in the search process. Try again.\n"

        filename = msg['result']['file']['name']+ "." + msg['result']['file']['ext']
        if(str2Bool(msg['result']['existFile']) and msg['result']['occr'] != -1):
            return "File \'"+ filename + "\' found!\nNumber of times that \'" + msg['result']['word'] + "\' appears: " + msg['result']['occr'] + "\n"
        else:
            return "File \'"+ filename + "\' not found!\n"

    elif("action" in msg.keys()):
        if(msg['action'] == 'sch'):
            filename = msg['file']['name'] + "." + msg['file']['ext']
            return "The request to search \'" + msg['word'] + "\' in \'" + filename + "\' received. Searching...\n"

    else:
        return "Can't interpret message! Try to search again!\n"