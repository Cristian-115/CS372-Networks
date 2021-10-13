import socket
import sys

#sources are cited in the pdf too
#source:
#https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket 

host = "gaia.cs.umass.edu"
s.connect((host, 80)) #connect our socket to the host and default port
request =  "GET /wireshark-labs/HTTP-wireshark-file3.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"

print("Request:", request)

s.send(request.encode()) #encode the ur and sent it


while True: #infinite while loop to ensure all teh data is read
    portion = s.recv(5098) #get the first chunk of data 
    print("[RECV] - length:", len(portion))
    if not portion:# if there is no more data to rec break the loop
        break  
    print(portion.decode('UTF-8')) #decode and print the data
s.close()


    