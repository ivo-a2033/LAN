import socket
import threading
import random
import pickle
import time
import pygame as pg
import sys

#---Game Data---

global bushes
bushes = []

global bullets 
bullets = []

for i in range(10):
    bush = pg.Vector2(random.randint(0,1440), random.randint(0,720))
    bushes.append(bush)


player_dict = {
    0: {"Pos": pg.Vector2(0,0),
        "Image": 0},
    1: {"Pos": pg.Vector2(0,0),
        "Image": 0},
}



def exchange_data(conn, ID):
    global bushes
    global bullets

    while True:
        time.sleep(0.02)

        try: # Check if the client killed the process

            #Receive data
            received = conn.recv(8192)
            data = pickle.loads(received)
            greeting = data["Greeting"]
            player_data = data["Player"]
            id_ = data["ID"]
            commands = data["Commands"]


            for command in commands:
                if command == "Shoot":
                    bullets.append(player_data["Pos"])
                    if len(bullets) > 200:
                        bullets.pop(0)
            commands = []
            
            #Update player pos data
            player_dict[id_] = player_data

            #Check if the connection was closed properly
            if greeting == "close":
                print("Connection closed")
                break

            else: # Respond if connection is still on
                message = {
                    "Greeting": "response" + str(ID),
                    "Bushes": bushes,
                    "Players": player_dict,
                    "Bullets": bullets
                }
                print("sent response to", str(ID))
                conn.send(pickle.dumps(message))

        except ConnectionResetError:
            print("Connection closed")
            break
        except Exception as e:
            print(e)

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

