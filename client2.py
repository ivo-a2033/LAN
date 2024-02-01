import socket, pickle
import threading
import pygame as pg
import player
import time

HOST = 'localhost'
PORT = 9080

# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

global still_on
still_on = True

#---Game Data---
game_data = {}

global player_pos
player_pos = pg.Vector2(720,560)

def exchange_data():
    global game_data
    global player_pos

    while still_on:
        time.sleep(0.02)
        # Send to server
        my_message = pickle.dumps({
            "Greeting": "greeting",
            "Player": player_pos,
            "ID": 1
        })
        s.send(my_message)
        # Receive response
        message = s.recv(4096)
        game_data = pickle.loads(message)
       

    s.send(pickle.dumps({
            "Greeting": "close",
            "Player": player_pos,
            "ID": 1
        }))

    s.close()

new_thread = threading.Thread(target=exchange_data)
new_thread.start()

class Game():
    def __init__(self) -> None:
        self.display = pg.display.set_mode((1440,720))
        print(self.display)

        self.player = player.Player(self.display, pg.Vector2(720,560))
        self.running = True
        self.clock = pg.time.Clock()

    def run(self):
        global still_on
        global game_data
        global player_pos

        while self.running:
            self.display.fill((25,25,25))

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                    still_on = False

            if len(game_data) != 0:
                print(game_data["Greeting"])
                bushes = game_data["Bushes"]
                for b in bushes:
                    pg.draw.circle(self.display, (100,200,100), b, 10)
                for p in game_data["Players"].keys():
                    pg.draw.circle(self.display, (100,100,200), game_data["Players"][p], 10)

            self.player.debug_draw()
            keys_pressed = pg.key.get_pressed()
            self.player.get_input(keys_pressed)
            player_pos = self.player.pos


            self.clock.tick(60)
            pg.display.update()

game = Game()
game.run()