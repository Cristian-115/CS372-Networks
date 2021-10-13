import socket
import sys


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create the socket

host = "gaia.cs.umass.edu"
s.connect((host, 80)) #connect to gaia with the defualt port 80 for http
request = "GET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n" #this is the url we will be requesting
print("Request:", request) #print the urn

s.send(request.encode())  #send over the encoded url
    # receive some data 
response = s.recv(4096)  #rec the encoded reponse      
  

 #display the response
print("[RECV] - length:", len(response))
print(response.decode('UTF-8')) #print the response and decode it so its readable
s.close()
    