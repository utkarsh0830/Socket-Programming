import socket
import sys

def createSocket():
    try:
        global s, host, port
        host = "0.0.0.0"
        port = 9989
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created")
    except socket.error as msg:
        print("Socket Creation error: " + str(msg))
        sys.exit(1)

def bindSocket():
    try:
        global s, host, port
        print("Binding the Port: " + str(port))
        s.bind((host, port))
        s.listen(5)
        print("Listening...")
    except socket.error as msg:
        print("Socket Binding error: " + str(msg))
        s.close()
        sys.exit(1)

def socketAccept():
    conn, address = s.accept()
    print("Connection established | IP " + address[0] + " | Port " + str(address[1]))
    sendCommands(conn)
    conn.close()

def sendCommands(conn):
    while True:
        cmd = input("> ")
        if cmd.lower() == "quit":
            conn.close()
            s.close()
            sys.exit(0)

        if len(cmd.strip()) > 0:
            conn.send(cmd.encode("utf-8"))
            
            response = b""
            conn.settimeout(1.0)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    response += chunk
            except socket.timeout:
                pass

            print(response.decode("utf-8"), end="")

def main():
    createSocket()
    bindSocket()
    socketAccept()

main()
