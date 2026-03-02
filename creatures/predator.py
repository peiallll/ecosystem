import settings as set
import pygame as pg
import random as r

pg.mixer.init()

class Predator:
    counter = 0
    def __init__(self, x, y):
        self.name = f"Prey{Predator.counter}"
        Predator.counter += 1

        self.x = x
        self.y = y

        self.speed = 2.5
        self.colour = (125, 0, 0)
        self.radius = set.predator_radius
        self.age = 0

        self.max_energy = 150
        self.energy = 100
        self.is_alive = True

        self.rep_cooldown = set.pred_rep_cooldown
        self.waiting_for_mate = False
        self.mate_target = None
        self.mate_timer = 15

        self.target_x = r.randint(0, set.screen_width)
        self.target_y = r.randint(0, set.screen_height)

    def pred_wander(self):
        self.target_x = r.randint(0, set.screen_width)
        self.target_y = r.randint(0, set.screen_height)

    def update(self):
            # calculate distance to target (pythagoras)
        dx = self.target_x - self.x 
        dy = self.target_y - self.y  
        dist_to_target = (dx**2 + dy**2)**0.5

        if dist_to_target < 2:
            # snap to target
            self.x = self.target_x
            self.y = self.target_y

            self.pred_wander()
        else:
            # slowdown as it approaches target
            k = 50  
            step = self.speed * (dist_to_target / (dist_to_target + k))

            self.prev_x = self.x
            self.prev_y = self.y

            self.x += (dx / dist_to_target) * step
            self.y += (dy / dist_to_target) * step

    def draw(self, surface):
        pg.draw.circle(surface, self.colour, (self.x, self.y), self.radius)