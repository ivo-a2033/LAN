import pygame as pg


class Player():
    def __init__(self, display, pos: pg.Vector2) -> None:
        self.display = display
        self.pos = pos
        self.camera = pg.Vector2(0,0)

    def debug_draw(self):
        pg.draw.circle(self.display, (255,0,0), self.pos - self.camera, 5)
    
    def get_input(self,keys_pressed):
        if keys_pressed[pg.K_w]:
            self.pos.y -= 1