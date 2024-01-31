import socket, pickle
import threading
import pygame as pg

HOST = 'localhost'
PORT = 8080

# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

global still_on
still_on = True

def exchange_data():
    while still_on:
        # Send to server
        s.send(("request").encode("utf-8"))
        # Receive response
        data = s.recv(4096).decode("utf-8")
        print(data)

    s.send(("close").encode("utf-8"))

    s.close()

new_thread = threading.Thread(target=exchange_data)
new_thread.start()

class Game():
    def __init__(self) -> None:
        self.display = pg.display.set_mode((1600,720))

        self.running = True
        self.clock = pg.time.Clock()

    def run(self):
        global still_on

        while self.running:
            self.display.fill((25,25,25))

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                    still_on = False
            
            pg.display.update()

game = Game()
game.run()