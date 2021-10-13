  
import socket
import sys
from random import seed
from random import randint




host = socket.gethostname()
port = 4112 
s = socket.socket() #1.	The server creates a socket 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#Make it so we can reuse the same addr
s.bind((host, port)) #binds to ‘localhost’ and port xxxx


s.listen(2)# 2.	The server then listens for a connection
conn, address = s.accept() #accept the connection
print("Connection by: " + str(address))
print('waiting for message .....')
data = conn.recv(2000).decode() #the server calls recv to receive data

print('Type /q to quit')    
while True:#Back to step 3
    if data == "": break
    data = conn.recv(1024).decode()
    print("Received from client: " + str(data))#The server prints the data
    data = input('Server: ')#then prompts for a reply
    conn.send(data.encode())  #Otherwise, the server sends the reply
    if data == "/q": break

conn.close()#Sockets are closed