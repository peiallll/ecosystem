import random as r
import pygame as pg
from settings import screen_width, screen_height

class Prey:
    counter = 0

    def __init__(self, x, y):
        self.name = f"Prey{Prey.counter}"
        Prey.counter += 1

        self.x = x
        self.y = y
        self.speed = 2
        self.colour = (127, 127, 127)
        self.radius = 10
        self.age = 0

        # energy levels
        self.max_energy = 100
        self.energy = 50
        self.is_alive = True
        
        # resting state
        self.resting = False
        self.rest_timer = 0

        # initial target
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"{self.name} travelling to ({self.target_x}, {self.target_y})..")

    def choose_random_target(self, screen_width, screen_height):
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"{self.name} travelling to ({self.target_x}, {self.target_y})..")

    def update(self, dt, screen_width, screen_height):
        self.age += 1 * dt

        self.energy -= 1.5 * dt
        self.energy = max(0, self.energy)

        ratio = self.energy / self.max_energy
        shade = int(ratio * 255)
        
        self.colour = (shade, shade, shade)

        if self.energy <= 0:
            self.die()
            if not self.is_alive:
                print(f"\033[91m{self.name} has died! (age {int(self.age)})\033[0m")
            return
    
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
                print(f"{self.name} resting for {round(self.rest_timer/60, 2)} seconds..")

            # pick new target
            self.choose_random_target(screen_width, screen_height)
        else:
            # slowdown as it approaches target
            k = 50  # tweak this for how early it starts slowing
            step = self.speed * (distance / (distance + k))

            # move along vector
            self.x += (dx / distance) * step
            self.y += (dy / distance) * step


    def die(self):
        self.speed = 0
        if self.radius > 0:
            self.radius -= 0.1

        else:
            self.is_alive = False

    def draw(self, surface):
        pg.draw.circle(surface, self.colour, (self.x, self.y), self.radius)