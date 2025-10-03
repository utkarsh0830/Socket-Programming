
import socket
import struct

def createSocket():

    try:
        global s,host,port
        host = "0.0.0.0"
        port = 9990
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Socket Created ")

    except socket.error as msg:
        print("Socket creation failed: " + str(msg)) 

def bindSocket():
    try:
        global s,host,port
        s.bind((host,port))
        s.listen(2)

        print(f"Server Listening on port: {port}")

    except socket.error as msg:
        print("Socket Binding failed " + str(msg))

def handleClient(conn,addr):

    while True:
        
        data = conn.recv(2)

        if not data:
            break

        num1,num2 = struct.unpack("BB",data)
        print(f"Received number from client: {num1}, {num2}")

        mul = num1 * num2

        resStr = str(num1) + str(mul) + str(num2)

        result = int(resStr)
        print(f"Result formed: {result}")

        conn.send(struct.pack("H",result))

    conn.close()

def main():
    createSocket()
    bindSocket()

    while True:
        conn,addr = s.accept()
        handleClient(conn,addr)

main()
