import socket
import threading
import random
import pickle
import time
import pygame

#---Game Data---

global bushes
bushes = []

for i in range(10):
    bush = [random.randint(0,1440), random.randint(0,720)]
    bushes.append(bush)


player_dict = {
    0: pygame.Vector2(0,0),
    1: pygame.Vector2(0,0),
}

def exchange_data(conn, ID):
    global bushes

    while True:
        time.sleep(0.02)

        try: # Check if the client killed the process

            #Receive data
            data = pickle.loads(conn.recv(4096))
            greeting = data["Greeting"]
            player_pos = data["Player"]
            id_ = data["ID"]

            #Update player pos data
            player_dict[id_] = player_pos

            #Check if the connection was closed properly
            if greeting == "close":
                print("Connection closed")
                break

            else: # Respond if connection is still on
                message = {
                    "Greeting": "response" + str(ID),
                    "Bushes": bushes,
                    "Players": player_dict
                }
                print("sent response to", str(ID))
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

