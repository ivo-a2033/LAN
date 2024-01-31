import socket
import threading
import random
import pickle
import time

#---Game Data---

global bushes
bushes = []

for i in range(10):
    bush = [random.randint(0,1440), random.randint(0,720)]
    bushes.append(bush)

def exchange_data(conn, ID):
    global bushes

    while True:
        time.sleep(0.02)
        try: #Check if the client killed the process
            data = conn.recv(4096).decode("utf-8")

            #Check if the connection was closed properly
            if data == "close":
                print("Connection closed")
                break
            else: # Respond if connection is still on
                #print(data)

                message = []
                message.append("response" + str(ID))
                print("sent response to", str(ID))
                message.append(bushes)
                conn.send(pickle.dumps(message))

        except ConnectionResetError:
            print("Connection closed")
            break
    conn.close()

def handle_client(s, ID):
    conn, addr = s.accept()
    print('Connected by', addr)
    conns.append(conn)
    exchange_data(conn, ID)

HOST = 'localhost'
PORTS = [8080, 9080]  # Adjust the ports as needed

sockets = []
conns = []

for port in PORTS:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.listen()
    sockets.append(s)

try:
    id_ = 0
    print("Listening...")
    while True:
        time.sleep(0.02)
        for s in sockets:
            id_ += 1
            threading.Thread(target=handle_client, args=(s, id_)).start()
            sockets.remove(s)
            print("thread created")
            print(id_)

        for b in range(len(bushes)):
            new_bush = bushes[b]
            new_bush[0] += 1
            bushes[b] = new_bush

except KeyboardInterrupt:
    print("Server shutting down.")
    for conn in conns:
        conn.close()

