import socket
import threading

groups = {}  #groupId --> (conn,userId)
groupLock = threading.Lock()

def createSocket():
    global s,host,port 
    host = '0.0.0.0'
    port = 9991

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def bindSocket():
    global host,port 
    s.bind((host,port))
    s.listen(5)
    print(f"Listening on {host}:{port}")

def registerUser(conn):
    
    conn.sendall("Enter User Id: ".encode('utf-8'))
    userId = conn.recv(1024).decode().strip()
    if(not userId):
        return (None,None)

    conn.sendall("Enter Group Id: ".encode('utf-8'))
    groupId = conn.recv(1024).decode().strip()
    if not groupId:
        return (None,None)
    
    with groupLock:
        if groupId not in groups:
            groups[groupId] = []

        groups[groupId].append((conn,userId))

    message = f"Connected with groupId : {groupId} "
    conn.send(message.encode('utf-8'))
    return (groupId,userId)

def unregisterUser(conn,userId,groupId):
    with groupLock:
        if groupId in groups:
            newList = []
            for (c,u) in groups[groupId]:
                if c != conn:
                    newList.append((c,u))

            groups[groupId] = newList
            conn.sendall(f"U are removed from the group Id: {groupId}".encode('utf-8'))

        if len(groups[groupId]) == 0:
            del groups[groupId]


def relayMessage(senderConn,userId,groupId,msg):
    with groupLock:
        members = groups.get(groupId,[]).copy()


    for (c,u) in members:
        if(c != senderConn):
            c.sendall(f"Sender {userId}: {msg}".encode('utf-8'))
    

def handleClient(conn,addr):
    
    groupId,userId = registerUser(conn)
    print(f"Group Id: {groupId} : {userId}")

    try:
        while True:
            data = conn.recv(2048).decode('utf-8')
            if not data:
                conn.close()
                break

            relayMessage(conn,userId,groupId,data)
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