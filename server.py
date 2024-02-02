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
    bush = [random.randint(0,1440), random.randint(0,720)]
    bushes.append(bush)


player_dict = {
    0: {"Pos": (0,0),
        "Image": 0},
    1: {"Pos": (0,0),
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
                name, argument = command
                if name == "Shoot":
                    bullets.append([player_data["Pos"][0], player_data["Pos"][1], argument[0], argument[1]])
                    if len(bullets) > 150:
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
                #print("sent response to", str(ID))
                to_send = pickle.dumps(message)
                conn.send(to_send)
                print(sys.getsizeof(to_send), " bytes sent")
                print(len(bullets), " bullets")
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

        
        for bullet in bullets:
            bullet[0] += bullet[2] * 400/60
            bullet[1] += bullet[3] * 400/60

except KeyboardInterrupt:
    print("Server shutting down.")
    for conn in conns:
        conn.close()

