import socket, pickle
import threading
import pygame as pg
import player
import time
import math
from utils import fps, delta, message_buffer
import random

HOST = '192.168.1.102'
PORT = 8080

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
    0: pg.transform.scale(pg.image.load("images_transparent/guy.png"), pg.Vector2(32,32)),
}

item_imgs = {
    0: pg.transform.scale(pg.image.load("images_transparent/handgun.png"), pg.Vector2(32,32)),
    1: pg.transform.scale(pg.image.load("images_transparent/blueGem.png"), pg.Vector2(32,32)),
    2: pg.transform.scale(pg.image.load("images_transparent/redCrystal.png"), pg.Vector2(32,32)),
    3: pg.transform.scale(pg.image.load("images_transparent/shotgun.png"), pg.Vector2(32,32)),

}

global commands
commands = []
global my_id
my_id = 0

pg.mixer.init()
oof = pg.mixer.Sound("oof.wav")


def exchange_data():
    global game_data
    global player_pos
    global commands
    global my_id

    while still_on:
        time.sleep(0.02)
        # Send to server
        try:
            my_message = pickle.dumps({
                "Greeting": "greeting",
                "Player": {
                    "Pos": (player_pos.x, player_pos.y),
                    "Image": 0},
                "ID": my_id,
                "Commands": commands
            })
        except Exception as e:
            print(e)
        commands = []
        s.send(my_message)
        # Receive response

        message = s.recv(message_buffer)
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
                "ID": my_id,
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

        bush1 = pg.transform.scale(pg.image.load("images_transparent/bush1.png"), pg.Vector2(128,128))
        bush2 = pg.transform.scale(pg.image.load("images_transparent/bush2.png"), pg.Vector2(128,128))

        bush1B = pg.transform.scale(pg.image.load("images_transparent/bush1transparent.png").convert_alpha(), pg.Vector2(128,128))
        bush2B = pg.transform.scale(pg.image.load("images_transparent/bush2transparent.png").convert_alpha(), pg.Vector2(128,128))

        self.bushes = [bush1, bush2]
        self.bushes_transparent = [bush1B, bush2B]

        self.rocket = pg.transform.scale(pg.image.load("images_transparent/rocket.png").convert_alpha(), pg.Vector2(16,16))
        self.gun = pg.transform.scale(pg.image.load("images_transparent/handgun.png").convert_alpha(), pg.Vector2(32,32))

        self.reloading = 0
        self.reload_time = .8
        self.ammo = 6
        self.my_ammo = 24

        self.has_gun = False
        self.has_shotgun = False

        self.player.pos.x += 3000 
        self.player.camera.x += 3000

    def run(self):
        global still_on
        global game_data
        global player_pos
        global commands
        global my_id

        while self.running:
            self.display.fill((71,45,60))
            mox, moy = (pg.mouse.get_pos() + self.player.camera)

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                    still_on = False
                if e.type == pg.MOUSEBUTTONDOWN:
                    if self.has_gun or self.has_shotgun:
                        if e.button == 1 and self.ammo > 0:
                            self.ammo -= 1
                            pointing_direction = math.atan2(moy - self.player.pos.y + 32, mox - self.player.pos.x)
                            commands.append(("Shoot", [math.cos(pointing_direction), math.sin(pointing_direction)]))
                            if self.has_shotgun:
                                for i in range(3):
                                    pointing_direction = math.atan2(moy - self.player.pos.y + 32, mox - self.player.pos.x) + random.uniform(-.5,.5)
                                    commands.append(("Shoot", [math.cos(pointing_direction), math.sin(pointing_direction)]))
                        if e.button == 3 and self.my_ammo > 0:
                            self.reloading = self.reload_time

            if self.player.hp <= 0:
                self.running = False
                still_on = False

            if self.reloading > 0:
                pg.draw.arc(self.display, (255,255,255), (self.player.pos - pg.Vector2(48,48) - self.player.camera, (96,96)), 0, self.reloading/self.reload_time*math.pi*2, 1)
                self.reloading -= delta
                if self.reloading <= 0:
                    self.reloading = 0
                    self.ammo = min(self.my_ammo,6)
                    self.my_ammo -= self.ammo

            if len(game_data) != 0:
                #Print the greeting
                #print(game_data["Greeting"], pg.time.get_ticks())

                #Get and draw items, check picking up
                items = game_data["Items"]
                for item in items:
                    if (self.player.pos - pg.Vector2(item[0],item[1])).length() < 32:
                        commands.append(("PickUp", [item[0],item[1]]))
                        if item[3] == 0:
                            self.has_gun = True
                        if item[3] == 1:
                            self.player.speed_boost += .4
                        if item[3] == 2:
                            self.my_ammo += 8
                        if item[3] == 3:
                            self.has_shotgun = True
                            self.has_gun = False
                    self.display.blit(item_imgs[item[3]], pg.Vector2(item[0], item[1]) - self.player.camera - pg.Vector2(16,16))

                #Get and draw bullets
                bullets = game_data["Bullets"]
                for bullet in bullets:
                    angle = -math.atan2(bullet[3], bullet[2])/math.pi*180 - 45
                    img = pg.transform.rotate(self.rocket, angle)
                    self.display.blit(img, pg.Vector2(bullet[0], bullet[1]) - self.player.camera - pg.Vector2(8,8))
                    if bullet[4][1] != my_id:
                        if abs(bullet[0] - self.player.pos.x) < 24 and abs(bullet[1] - self.player.pos.y) < 24:
                            commands.append(("Remove", bullet[4]))
                            self.player.hp -= 33
                            oof.play()


                #Get and draw players
                for p in game_data["Players"].keys():
                    if p != my_id:
                        player_data = game_data["Players"][p]
                        pos = player_data["Pos"]
                        img = images_dict[player_data["Image"]]
                        self.display.blit(img, pos - self.player.camera - pg.Vector2(16,16))

            keys_pressed = pg.key.get_pressed()
            self.player.get_input(keys_pressed)
            self.player.move()
            self.player.draw(self.has_gun, self.has_shotgun)
            player_pos = self.player.pos

 

            for i in range(self.my_ammo):
                pg.draw.rect(self.display, (255,255,255), (10+i*3, 52, 2, 6))

            if len(game_data) != 0:
                #Get and draw bushes
                bushes = game_data["Bushes"]
                for b in bushes:
                    if (self.player.pos - pg.Vector2(b[0],b[1])).length() < 40:
                        self.display.blit(self.bushes_transparent[b[2]], pg.Vector2(b[0],b[1]) - self.player.camera - pg.Vector2(64,64))
                    else:
                        self.display.blit(self.bushes[b[2]], pg.Vector2(b[0]-64, b[1]-64) - self.player.camera)

            pg.draw.rect(self.display, (200,100,100), (pg.Vector2(-1440*2.5, -720*2.5) - self.player.camera, (1440 * 6, 720 * 6)), 2)
            self.clock.tick(fps)
            pg.display.update()

game = Game()
game.run()