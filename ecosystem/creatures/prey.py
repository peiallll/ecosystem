import random as r
import pygame as pg
from settings import screen_width, screen_height

class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.colour = (83, 83, 252)
        self.radius = 10

        # resting state
        self.resting = False
        self.rest_timer = 0

        # initial target
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"Prey travelling to ({self.target_x}, {self.target_y})..")

    def choose_random_target(self, screen_width, screen_height):
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"Prey travelling to ({self.target_x}, {self.target_y})..")

    def move(self, screen_width, screen_height):
        # handle resting
        if self.resting:
            self.rest_timer -= 1
            if self.rest_timer <= 0:
                self.resting = False
            return  # skip movement while resting

        # calculate distance to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance < 0.1:
            # snap to target
            self.x = self.target_x
            self.y = self.target_y

            # 1/3 chance to rest
            if r.randint(1,3) == 1:
                self.resting = True
                self.rest_timer = r.randint(90, 220)  # frames to rest
                print(f"Prey resting for {round(self.rest_timer/60, 2)} seconds..")

            # pick new target
            self.choose_random_target(screen_width, screen_height)
        else:
            # slowdown as it approaches target
            k = 50  # tweak this for how early it starts slowing
            step = self.speed * (distance / (distance + k))

            # move along vector
            self.x += (dx / distance) * step
            self.y += (dy / distance) * step

    def draw(self, surface):
        pg.draw.circle(surface, self.colour, (self.x, self.y), self.radius)