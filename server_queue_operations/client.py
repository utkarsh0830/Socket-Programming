import socket,struct

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
host = "10.112.194.233"
port = 9991

while True:

    cmd = input("Enter operation: ")

    if(cmd.lower() == "quit"): break

    queueId = int(input("Enter Queue Id: "))
    opcode = 0
    message = ""

    if(cmd.lower() == "push"):
        opcode = 1
        message = input("Enter message want to insert in queue: ")

    elif (cmd.lower() == "pop"):
        opcode = 2

    elif (cmd.lower() == "peek"):
        opcode = 3

    elif (cmd.lower() == "echo"):
        message = input("Enter message to echo: ")
        opcode = 4

    else:
        print("Invalid Operation: ")
        continue

    msgBytes = message.encode('utf-8')
    msgSize = len(msgBytes)

    packet = struct.pack("BBB",opcode,queueId,msgSize) + msgBytes

    s.sendto(packet,(host,port))

    data,addr = s.recvfrom(1024)

    print(f"Server Response: {data.decode('utf-8')}")

    





