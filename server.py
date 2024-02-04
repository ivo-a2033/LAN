import socket
import threading
import random
import pickle
import time
import sys
from utils import delta, message_buffer

#---Game Data---

global bushes
bushes = []

global bullets 
bullets = []

global items
items = []

screen_wid = 1440
screen_ht = 720

for i in range(20):
    bush = [random.uniform(-screen_wid*.5,screen_wid*1.5), random.uniform(-screen_ht*.5,screen_ht*1.5), random.randint(0,1)]
    bushes.append(bush)

#IDs
#--Gun: 0
for i in range(4):
    gun = [random.uniform(-screen_wid*.5,screen_wid*1.5), random.uniform(-screen_ht*.5,screen_ht*1.5), random.randint(0,1), 0]
    items.append(gun)

    gem = [random.uniform(-screen_wid*.5,screen_wid*1.5), random.uniform(-screen_ht*.5,screen_ht*1.5), random.randint(0,1), 1]
    items.append(gem)

    ammo = [random.uniform(-screen_wid*.5,screen_wid*1.5), random.uniform(-screen_ht*.5,screen_ht*1.5), random.randint(0,1), 2]
    items.append(ammo)



player_dict = {
    0: {"Pos": (0,0),
        "Image": 0},
    1: {"Pos": (0,0),
        "Image": 0},
}



def exchange_data(conn, ID):
    global bushes
    global bullets
    bullet_id = 0

    while True:
        time.sleep(0.02)

        try: # Check if the client killed the process

            #Receive data
            received = conn.recv(message_buffer)
            data = pickle.loads(received)
            greeting = data["Greeting"]
            player_data = data["Player"]
            id_ = data["ID"]
            commands = data["Commands"]


            for command in commands:
                name, argument = command
                if name == "Shoot":
                    bullets.append([player_data["Pos"][0], player_data["Pos"][1] - 32, argument[0], argument[1], [bullet_id, id_]])
                    bullet_id += 1
                    if len(bullets) > 50:
                        bullets.pop(0)
                if name == "PickUp":
                    for item in items:
                        if [item[0], item[1]] == argument:
                            items.remove(item)
                if name == "Remove":
                    for bullet in bullets:
                        if bullet[4] == argument:
                            bullets.remove(bullet)

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
                    "Bullets": bullets,
                    "Items": items

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

HOST = '192.168.1.102'
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
        time.sleep(0.01)
        for s in sockets:
            id_ += 1
            threading.Thread(target=handle_client, args=(s, id_)).start()
            sockets.remove(s)
            print("thread created")
            print(id_)

        
        for bullet in bullets:
            bullet[0] += bullet[2] * 400 * delta
            bullet[1] += bullet[3] * 400 * delta

except KeyboardInterrupt:
    print("Server shutting down.")
    for conn in conns:
        conn.close()

