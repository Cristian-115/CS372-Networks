import socket
import sys
  
#sources are cited in the pdf too
#source:
# https://zetcode.com/python/socket/#:~:text=The%20recv()%20method%20receives,returns%20an%20empty%20byte%20string


port = 5001#random port

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
socket.bind(('127.0.0.1',port)) #bind the socket to host and the port

data = "HTTP/1.1 200 OK\r\n"\ 
"Content-Type: text/html; charset=UTF-8\r\n\r\n"\
"<html>Congratulations! You've downloaded the first Wireshark lab file!</html>\r\n" #this is the data we will be sending to the server 

socket.listen(5) #wait for a connection to be made
print("server is listening...")
while True:
    connection, address = socket.accept() #acceot the connection
    serverData = connection.recv(1024) #recv the data from the server
    print("Recieved:", serverData)
    serverData = data
    connection.send(serverData.encode())
    print(data) 
    connection.close() #close socket
    break