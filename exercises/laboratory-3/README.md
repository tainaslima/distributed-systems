# Laboratory 3

> This repository contains all implementations made for laboratory 3, in which we had to evolve our laboratory 2 server code to a concurrent server which can also read some "adm" commands from its standard input. In my case, I used the Thread implementation avaiable in the ```threading``` Python library. The client's code is the same from laboratory 2.

## Organization
- ```server.py``` contains the server side's layers (a part of the processing layer and database access layer)
    - Process layer: Encode/decode messages and search for the word sent by the user in the specified file
    - Database layer: Get the text from files or returns an error message if the file doesn't exist
- ```client.py```contains contais the client side's layers (a part of the processing layer and interface layer)
    - Process layer: Encode/decode messages
    - Interface layer: Convert the result messages in more readable messages for user and deal with all interactions between user and the app
- ```messageProtocol.py``` contains methods related to the messages convertion protocol (encode and decode message, interpret message, etc)
- ```\database``` is a folder which contains the files which the server can access

## How to run
First, you must have at least 2 terminals open: one to run the server and the other, the client. After opening them, run the file ```server.py``` first in one terminal and then run ```client.py``` in the other. 
In the client's side, the app will show a menu asking what action do you want to take, type 1 if you want to search for a word in a file. The app will ask for the filename (IMPORTANT: YOU MUST TYPE THE FILENAME WITH ITS EXTENSION!) and the word to be searched.
If this file exists in the database, the server will inform the client that the file exist and the word's counting in that file. This information will be printed to user and the app will ask what does the user want to do again, until the user types 0 to end the app.

In the server's side, if you want to execute some "adm" commands, you can just type in the server's terminal one of the commands bellow:
- kill: to kill the server
- count_workers: to count active threads
- historical_clients: to show in terminal all clients address who connected with the server.


## Built with
- Python 3.x + libraries
- Visual Studio Code
- Windows 10

## Meta
Tainá Lima - tainaslima19@gmail.com

[https://github.com/tainaslima/](https://github.com/tainaslima/)
