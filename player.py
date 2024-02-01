import pygame as pg

delta = 1/60

class Player():
    def __init__(self, display, pos: pg.Vector2) -> None:
        self.display = display
        self.pos = pos
        self.camera = pg.Vector2(0,0)

        self.velocity = pg.Vector2(0,0)
        self.speed = 150

        self.img = pg.image.load("images/guy.png")
        self.img = pg.transform.scale(self.img, pg.Vector2(32,32))
        self.size = pg.Vector2(self.img.get_width(), self.img.get_height())

    def debug_draw(self):
        pg.draw.circle(self.display, (255,0,0), self.pos - self.camera, 5)

    def draw(self):
        self.display.blit(self.img, self.pos - self.size/2 - self.camera)
    
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