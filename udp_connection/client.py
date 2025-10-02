
import socket


host = "10.112.194.233"
port = 9995

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

while(True):
    msg = input("Enter message (type 'quit' to exit):")

    if(msg.lower() == "quit"):
        break;

    s.sendto(msg.encode('utf-8'),(host,port))
    data,addr = s.recvfrom(1024)

    print(f"Server echoed: {data.decode('utf-8')}")
