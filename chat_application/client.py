import socket
import threading

def receive_messages(sock):
    """Continuously receive messages from server"""
    while True:
        try:
            data = sock.recv(2048)
            if not data:
                print("\n[Disconnected from server]")
                break
            print(data.decode('utf-8'), end='')  
        except:
            break

def main():
    host = '127.0.0.1'  
    port = 9997       

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("[Connected to server]")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            if not msg:
                continue
            sock.sendall((msg + '\n').encode('utf-8'))
            if msg.lower() == '/quit':
                break
    except KeyboardInterrupt:
        print("\n[Client closed]")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
