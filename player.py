import pygame as pg
import math

delta = 1/60

class Player():
    def __init__(self, display, pos: pg.Vector2) -> None:
        self.display = display
        self.pos = pos
        self.camera = pg.Vector2(0,0)

        self.velocity = pg.Vector2(0,0)
        self.speed = 150
        
        self.hp = 100

        self.img = pg.image.load("images_transparent/guy.png")
        self.img = pg.transform.scale(self.img, pg.Vector2(32,32))
        self.size = pg.Vector2(self.img.get_width(), self.img.get_height())
        self.gun_img = pg.transform.scale(pg.image.load("images_transparent/handgun.png").convert_alpha(), pg.Vector2(32,32))

    def debug_draw(self):
        pg.draw.circle(self.display, (255,0,0), self.pos - self.camera, 5)

    def draw(self, has_gun):
        self.display.blit(self.img, self.pos - self.size/2 - self.camera)
        if has_gun:
            mox, moy = pg.mouse.get_pos() + self.camera
            pointing_direction = -math.atan2(moy - self.pos.y, mox - self.pos.x)/math.pi*180
            img = pg.transform.rotate(self.gun_img, pointing_direction)
            self.display.blit(img, self.pos - self.camera - pg.Vector2(img.get_width(), img.get_height())/2 + pg.Vector2(0, -32))
        
        pg.draw.rect(self.display, (225,225,225), (10,10,self.hp * 3,20))
    
    def get_input(self,keys_pressed):
        self.velocity *= 0
        if keys_pressed[pg.K_w]:
            self.velocity.y = -1
        if keys_pressed[pg.K_s]:
            self.velocity.y = 1
        if keys_pressed[pg.K_a]:
            self.velocity.x = -1
        if keys_pressed[pg.K_d]:
            self.velocity.x = 1
        
        if self.velocity.length() != 0:
            self.velocity.normalize_ip()
    
    def move(self):
        self.pos += self.velocity * self.speed * delta
        self.camera += self.velocity * self.speed * delta