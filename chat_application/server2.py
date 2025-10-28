import socket
import threading
import time
import os
import json
from collections import deque


groups = {}  #groupId --> (conn,userId)
groupLock = threading.Lock()
history = {}
historyLock = threading.Lock()
MAX_LENGTH = 1000
RETENTION_TIME = 15 * 60
DATA_DIR = 'chat_msg_persist'

def createSocket():
    global s,host,port 
    host = '0.0.0.0'
    port = 9996

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def bindSocket():
    global host,port 
    s.bind((host,port))
    s.listen(5)
    print(f"Listening on {host}:{port}")


def ensureDataDir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def getGroupFilesPath(groupId):
    return os.path.join(DATA_DIR,f"group_{groupId}.json")

def loadPersistentHistory():
    ensureDataDir()
    now = time.time()

    with historyLock:
        for fname in os.listdir(DATA_DIR):
            
            if not fname.startswith('group_') or not fname.endswith('.json'):
                continue

            groupId = fname[len('group_'):-len('.json')]

            path = getGroupFilesPath(groupId)

            dq = deque()
            with open(path,'r') as f:
                msgs = json.load(f)

            for item in msgs:
                ts = item.get('ts',0)
                if now - ts <= RETENTION_TIME:
                    dq.append((ts,item.get('user',""),item.get('msg',"")))

            if dq:
                history[groupId] = dq
            else:
                history[groupId] = deque()


def persistHistory(groupId):

    ensureDataDir()
    path = getGroupFilesPath(groupId)

    with historyLock:
        dq = history.get(groupId,deque()).copy()
    
    toSave = []
    now = time.time()
    for (ts,userId,msg) in dq:
        if(now - ts <= RETENTION_TIME):
            toSave.append({
                "ts" : ts,
                "user":userId,
                "msg":msg
                })
            
    with open(path,'w') as f:
        json.dump(toSave,f)

def pruneHistory(groupId):

    now = time.time()
    with historyLock:
        if groupId not in history:
            history[groupId] = deque()

        dq = history[groupId]
        while dq and (now - dq[0][0] > RETENTION_TIME):
            dq.popleft()

    persistHistory(groupId)

    


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

    pruneHistory(groupId)
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

    pruneHistory(groupId)


def unregisterUser(conn,userId,groupId):
    with groupLock:
        if groupId in groups:
            newList = []
            for (c,u) in groups[groupId]:
                if c != conn:
                    newList.append((c,u))

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

def load_on_startup():
    loadPersistentHistory()
    print("[+] Loaded persisted histories (recent messages only).")


def runServer():
    while True:
        conn,addr = s.accept()
        t = threading.Thread(target=handleClient,args=(conn,addr))
        t.start()

def main():
    createSocket()
    bindSocket()
    ensureDataDir()
    load_on_startup()
    runServer()
    

if __name__ == '__main__':
    main()