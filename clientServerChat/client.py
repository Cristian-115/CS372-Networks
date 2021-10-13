 
import socket
import sys

host = socket.gethostname()  # as both code is running on same pc
port = 4112  # socket server port number
    
c = socket.socket()#The client creates a socket
c.connect((host, port))  #connects to ‘localhost’ and port xxxx
print('Enter message to send...')

message = input("Client: ")  #2.When connected, the client prompts for a message to send
c.send(message.encode())
while message != '/q': #If the message is /q, the client quits
    c.send(message.encode())  #Otherwise, the client sends the message
    data = c.recv(1024).decode()  #The client calls recv to receive data
    if data == "/q":break 
    print('Received from server: ' + data)  #The client prints the data
    message = input("Client: ")  # again take input

c.close()  #Sockets are closed 