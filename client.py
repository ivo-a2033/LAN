import socket, pickle
import threading
import pygame as pg
import player
import time

HOST = 'localhost'
PORT = 8080

# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

global still_on
still_on = True

#---Game Data---
game_data = []

def exchange_data():
    global game_data

    while still_on:
        time.sleep(0.02)
        # Send to server
        s.send(("request").encode("utf-8"))
        # Receive response
        message = s.recv(4096)
        greeting, bushes = pickle.loads(message)
        game_data = [greeting, bushes]

    s.send(("close").encode("utf-8"))

    s.close()

new_thread = threading.Thread(target=exchange_data)
new_thread.start()

class Game():
    def __init__(self) -> None:
        self.display = pg.display.set_mode((1440,720))
        print(self.display)

        self.player = player.Player(self.display, pg.Vector2(720,360))
        self.running = True
        self.clock = pg.time.Clock()

    def run(self):
        global still_on
        global game_data

        while self.running:
            self.display.fill((25,25,25))

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                    still_on = False

            self.player.debug_draw()

            if len(game_data) != 0:
                print(game_data[0])
                bushes = game_data[1]
                for b in bushes:
                    pg.draw.circle(self.display, (100,200,100), b, 10)
            
            self.clock.tick(60)
            pg.display.update()

game = Game()
game.run()