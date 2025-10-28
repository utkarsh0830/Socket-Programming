import socket
import threading
import time
from collections import deque
groups = {}  #groupId --> (conn,userId)
groupLock = threading.Lock()
history = {}
historyLock = threading.Lock()
MAX_LENGTH = 1000

def createSocket():
    global s,host,port 
    host = '0.0.0.0'
    port = 9993

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def bindSocket():
    global host,port 
    s.bind((host,port))
    s.listen(5)
    print(f"Listening on {host}:{port}")

def registerUser(conn):
    
    conn.sendall("Enter User Id: \n".encode('utf-8'))
    userId = conn.recv(1024).decode().strip()
    if(not userId):
        return (None,None)

    conn.sendall("Enter Group Id: \n".encode('utf-8'))
    groupId = conn.recv(1024).decode().strip()
    if not groupId:
        return (None,None)
    
    with groupLock:
        if groupId not in groups:
            groups[groupId] = []

        groups[groupId].append((conn,userId))
    
    with historyLock:
        if groupId not in history:
            history[groupId] = deque()

    sendHistory(conn,groupId)

    message = f"Connected with groupId : {groupId}\n"
    conn.send(message.encode('utf-8'))
    return (groupId,userId)

def sendHistory(conn,groupId):

    with historyLock:
        msg = history.get(groupId,[]).copy()

    conn.sendall(b"--- Last messages in this group ---\n")

    for (ts,user,message) in msg:
        timeStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ts))
        conn.sendall(f"{timeStr} {user}: {message}\n".encode('utf-8'))

    conn.sendall(b"--- End of history ---\n")

def storeHistory(userId,groupId,msg):

    ts = time.time()
    with historyLock:
        if groupId not in history:
            history[groupId] = deque()

        history[groupId].append((ts,userId,msg))

        if len(history[groupId]) > MAX_LENGTH:
            history[groupId].popleft()


def unregisterUser(conn,userId,groupId):
    with groupLock:
        if groupId in groups:
            newList = []
            for (c,u) in groups[groupId]:
                if c != conn:
                    newList.append((c,userId))

            groups[groupId] = newList
            conn.sendall(f"U are removed from the group Id: {groupId}\n".encode('utf-8'))

        if len(groups[groupId]) == 0:
            del groups[groupId]


def relayMessage(senderConn,userId,groupId,msg):

    storeHistory(userId,groupId,msg)

    with groupLock:
        members = groups.get(groupId,[]).copy()


    for (c,u) in members:
        if(c != senderConn):
            c.sendall(f"Sender {userId}: {msg}\n".encode('utf-8'))
    

def handleClient(conn,addr):
    
    groupId,userId = registerUser(conn)
    print(f"Group Id: {groupId} : {userId}")

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                conn.close()
                break

            text = data.decode('utf-8').strip()
            if text.lower() == 'quit':
                break

            relayMessage(conn,userId,groupId,text)
    except Exception:
        print("sad")

    finally:
        unregisterUser(conn,userId,groupId)
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def runServer():
    while True:
        conn,addr = s.accept()
        t = threading.Thread(target=handleClient,args=(conn,addr))
        t.start()

def main():
    createSocket()
    bindSocket()
    runServer()

if __name__ == '__main__':
    main()