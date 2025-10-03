import socket
import struct

host = "10.112.194.233"
port = 9990

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

while True:
    try:
        num1 = int(input("Enter a number1: "))
        num2 = int(input("Enter a number2: "))

        if not (0 <= num1 <= 9 and 0 <= num2 <= 9):
                print("Enter single-digit numbers (0-9)")
                continue

        data = struct.pack("BB", num1, num2)

        s.send(data)

        response = s.recv(2)

        res = struct.unpack("H",response)[0]
        print(f"Server sent result: {res}")

    except KeyboardInterrupt:
        break

s.close()
