import socket, pickle
import threading
import pygame as pg
import player
import time
import math

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
player_pos = pg.Vector2(720,360)

images_dict = {
    0: pg.transform.scale(pg.image.load("images/guy.png"), pg.Vector2(32,32)),
}

global commands
commands = []

def exchange_data():
    global game_data
    global player_pos
    global commands

    while still_on:
        time.sleep(0.02)
        # Send to server
        try:
            my_message = pickle.dumps({
                "Greeting": "greeting",
                "Player": {
                    "Pos": (player_pos.x, player_pos.y),
                    "Image": 0},
                "ID": 1,
                "Commands": commands
            })
        except Exception as e:
            print(e)
        commands = []
        s.send(my_message)
        # Receive response

        initial = time.time_ns()
        message = s.recv(8192)
        print(time.time_ns() - initial)
        try:
            game_data = pickle.loads(message)
        except Exception as e:
            print(e)
       
    try:
        s.send(pickle.dumps({
                "Greeting": "close",
                "Player": {
                    "Pos": (0,0),
                    "Image": 0},
                "ID": 1,
                "Commands": commands
            }))
    except:
        pass

    s.close()

new_thread = threading.Thread(target=exchange_data)
new_thread.start()

class Game():
    def __init__(self) -> None:
        self.display = pg.display.set_mode((1440,720))

        self.player = player.Player(self.display, pg.Vector2(720,360))
        self.running = True
        self.clock = pg.time.Clock()

    def run(self):
        global still_on
        global game_data
        global player_pos
        global commands

        while self.running:
            self.display.fill((25,25,25))

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                    still_on = False

            if len(game_data) != 0:
                #Print the greeting
                #print(game_data["Greeting"], pg.time.get_ticks())

                #Get and draw bushes
                bushes = game_data["Bushes"]
                for b in bushes:
                    pg.draw.circle(self.display, (100,200,100), b - self.player.camera, 10)

                #Get and draw bullets
                bullets = game_data["Bullets"]
                for bullet in bullets:
                    pg.draw.circle(self.display, (100,100,100), pg.Vector2(bullet[0], bullet[1]) - self.player.camera, 2)

                #Get and draw players
                for p in game_data["Players"].keys():
                    player_data = game_data["Players"][p]
                    pos = player_data["Pos"]
                    img = images_dict[player_data["Image"]]
                    self.display.blit(img, pos - self.player.camera - pg.Vector2(16,16))

            self.player.debug_draw()
            keys_pressed = pg.key.get_pressed()
            self.player.get_input(keys_pressed)
            self.player.move()
            self.player.draw()
            player_pos = self.player.pos

            mox, moy = (pg.mouse.get_pos() - self.player.camera)

            if keys_pressed[pg.K_SPACE]:
                pointing_direction = math.atan2(moy - self.player.pos.y, mox - self.player.pos.x)
                commands.append(("Shoot", [math.cos(pointing_direction), math.sin(pointing_direction)]))


            self.clock.tick(60)
            pg.display.update()

game = Game()
game.run()