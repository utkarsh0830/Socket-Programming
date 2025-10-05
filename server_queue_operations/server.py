import socket
import struct
from collections import deque

def initialzeQueue():
    global queue

    queue = {i : deque() for i in range(0,255)}

def createUDPSocket():
    try:
        global host,s,port
        host = "0.0.0.0"
        port = 9991

        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        print("Socket Created Sussfully: ")

    except socket.error as msg:
        print("UDP Socket Creation Failed: " + str(msg))
        

def bindUDPSocket():
    try:
        global s, host, port
        s.bind((host,port))
        print(f"Server Listening on Port: {port}")
    
    except socket.error as msg:
        print("UDP Binding Failed: " + str(msg))
        

def handleClient(data,addr):

    opcode,queueId,msgSize = struct.unpack("BBB",data[:3])
    message = data[3:3 + msgSize].decode('utf-8') if msgSize > 0 else ""

    response = ""

    if(opcode == 1):
        queue[queueId].append(message)
        response = f"Message: {message} pushed to Queue {queueId}"

    elif (opcode == 2):
        if(queue[queueId]):
            popped_msg = queue[queueId].popleft()
            response = f"Popped: {popped_msg}"
        else:
            response = "Queue Empty"

    elif (opcode == 3):

        if(queue[queueId]):
            peek_msg = queue[queueId][0]
            response = f"Peeked msg: {peek_msg}"
        else:
            response = "Queue Empty"

    elif (opcode == 4):
        response = f"Echo: {message}"
    else:
        response = "Please give correct Opcode Value"

    s.sendto(response.encode('utf-8'),addr)

def runServer():
    while True:
        data,addr = s.recvfrom(1024)
        handleClient(data,addr)

def main():
    createUDPSocket()
    bindUDPSocket()
    initialzeQueue()
    runServer()

main()
