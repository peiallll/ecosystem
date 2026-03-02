import pygame as pg
import settings
import random as r
from system.lerp import lerp
import math

pg.font.init()

FONT = pg.font.SysFont(None, 24)
young = (255, 255, 255) # tint - when young
old = (120, 60, 20)

class Bush:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.berries = [True, True, True]
        # timer counting down from setting's value when bush isn't full
        self.regrow_timer = 0

        self.age = 0
        self.lifespan = r.randint(80,100)
        self.dead = False

        # track time since last prey visit/eat
        self.time_since_visit = 0

        self.seed_cooldown = r.uniform(settings.seed_cooldown_lower, settings.seed_cooldown_higher)
        self.seed_timer = self.seed_cooldown
        self.active_seeds = []

        self.images = {
            "111": pg.image.load("images/bush111.png").convert_alpha(),
            "110": pg.image.load("images/bush110.png").convert_alpha(),
            "101": pg.image.load("images/bush101.png").convert_alpha(),
            "100": pg.image.load("images/bush100.png").convert_alpha(),
            "011": pg.image.load("images/bush011.png").convert_alpha(),
            "010": pg.image.load("images/bush010.png").convert_alpha(),
            "001": pg.image.load("images/bush001.png").convert_alpha(),
            "000": pg.image.load("images/bush000.png").convert_alpha(),
        }

    def eat_berry(self, index):
        if 0 <= index < 3:
            self.berries[index] = False
            # reset visit timer whenever a berry is taken
            self.time_since_visit = 0

    def regrow_berry(self, index):
        if 0 <= index < 3:
            self.berries[index] = True

    def get_image(self):
        key = ''.join(['1' if b else '0' for b in self.berries])
        return self.images[key]
    
    def update(self, dt, bush_list):
        self.age += dt
        if self.age >= self.lifespan:
            self.dead = True

        self.seed_timer -= dt

        if self.seed_timer <= 0 and sum(self.berries) >= 2:  # seed handling 
            angle = r.uniform(0, 2 * math.pi)
            distance = r.uniform(25,40)

            seed = Seed(self.x, self.y, angle, distance, lifetime=2)
            self.active_seeds.append(seed)
            
            self.seed_timer = r.uniform(20,40)

        for seed in self.active_seeds[:]:
            seed.update(dt)

            if seed.lifetime <= 0:
                new_bush = Bush(seed.x, seed.y)
                new_bush.berries = [False, False, False] # new bush starts with no berries
                bush_list.append(new_bush)
                self.active_seeds.remove(seed)

        # increment abandonment timer
        self.time_since_visit += dt
        if self.time_since_visit >= settings.bush_abandon_time:
            # bush withers due to neglect
            self.dead = True
            return

        if self.berries.count(True) < 3:
            if self.regrow_timer <= 0:
                self.regrow_timer = settings.berry_regrowth_rate
            else:
                self.regrow_timer -= dt
                if self.regrow_timer <= 0:
                    for i, berry in enumerate(self.berries):
                        if not berry:
                            self.regrow_berry(i)
                            break
                    if self.berries.count(True) < 3:
                        self.regrow_timer = settings.berry_regrowth_rate
                    else:
                        self.regrow_timer = 0
        else:
            self.regrow_timer = 0

    def draw(self, surface):
        image = self.get_image()

        ratio = self.age / self.lifespan
        ratio = max(0, min(1, ratio))

        tint = (
            lerp(young[0], old[0], ratio),
            lerp(young[1], old[1], ratio),
            lerp(young[2], old[2], ratio)
        )

        tinted = image.copy()
        tinted.fill(tint, special_flags=pg.BLEND_MULT)

        scaled_image = pg.transform.scale(tinted, (180, 180))
        surface.blit(scaled_image, (self.x, self.y))

        if self.regrow_timer > 0:
            txt = FONT.render(str(int(self.regrow_timer)), True, (255, 255, 255))
            txt_rect = txt.get_rect(center=((self.x + settings.bush_size / 2) - 15, self.y + 82.5))
            surface.blit(txt, txt_rect)

        for seed in self.active_seeds:
            pg.draw.circle(
                surface,
                (0, 0, 0),
                (int(seed.x + 90), int(seed.y + 82.5)),
            3)           

class Seed:
    def __init__(self, x, y, angle, distance, lifetime=2):
        self.x = x
        self.y = y
        self.dx = math.cos(angle) * distance
        self.dy = math.sin(angle) * distance

        self.lifetime = lifetime

    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.x = max(0,min(settings.screen_width - 20, self.x))
        self.y = max(0,min(settings.screen_height - 20, self.y))
        self.lifetime -= dt