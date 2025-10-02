import socket

def createUDPSocket():

    try:
        global port,s,host

        port = 9995
        host = "0.0.0.0"
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        print("UDP Socket Created")

    except socket.error as msg:
        print("Socket creation Failed:" + str(msg))

def bindUDPSocket():

    try:
        global s,host,port

        s.bind((host,port))

        print(f"UDP server listening on {host}:{port}")
    except socket.error as msg:
        print("Socket Bind Failed " + str(msg))
        s.close()
        exit()

def udpServer():
    
    while True:
        msg, address = s.recvfrom(1024)

        print(f"Received from Clien: {msg.decode('utf-8')}")
        s.sendto(msg,address)

def main():
    createUDPSocket()
    bindUDPSocket()
    udpServer()

main()