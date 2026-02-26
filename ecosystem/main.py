import pygame as pg
import random as r
from settings import screen_width, screen_height, fps, background_colour, num_preys

from creatures.prey import Prey

pg.init()

screen = pg.display.set_mode((screen_width, screen_height))
clock = pg.time.Clock()
running = True

p = Prey(screen_width / 2, screen_height / 2)

prey_list = []
for _ in range(num_preys):
    x = r.randint(0, screen_width)
    y = r.randint(0, screen_height)
    prey_list.append(Prey(x,y))


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(background_colour)

    for prey in prey_list:
        prey.move(screen_width, screen_height)
        prey.draw(screen)  

    pg.display.flip()
    clock.tick(fps)