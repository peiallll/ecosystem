import random as r
import pygame as pg
from settings import screen_width, screen_height, energy_gain_lower, energy_gain_higher, eat_threshold, reproduction_cooldown, rep_energy_cost, prey_radius, min_rep_energy, passive_energy_loss, rest_energy_gain

BUSH_HALF = 90
from system.distance import distance

pg.mixer.init()

death_sfx = pg.mixer.Sound("sfx/death.wav")
eat_sfx = pg.mixer.Sound("sfx/eat.wav")
birth_sfx = pg.mixer.Sound("sfx/birth.wav")

awaiting_mate = []

class Prey:
    counter = 0
    def __init__(self, x, y):
        self.name = f"Prey{Prey.counter}"
        Prey.counter += 1

        self.x = x
        self.y = y
        self.prev_x = None
        self.prev_y = None

        self.speed = 2
        self.colour = (127, 127, 127)
        self.radius = prey_radius
        self.age = 0

        # energy levels
        self.max_energy = 100
        self.energy = 75
        self.is_alive = True
        
        # resting state
        self.resting = False
        self.rest_chance = 3
        self.rest_chance_updated = False
        self.rest_timer = 0

        #reproduction
        self.rep_cooldown = reproduction_cooldown
        self.waiting_for_mate = False
        self.mate_target = None
        self.mate_timer = 10

        # initial target
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"{self.name} travelling to ({self.target_x}, {self.target_y})..")        
        # bush assignment
        self.assigned_bush = None

    def choose_random_target(self, screen_width, screen_height):
        self.target_x = r.randint(self.radius, screen_width - self.radius)
        self.target_y = r.randint(self.radius, screen_height - self.radius)
        print(f"{self.name} travelling to ({self.target_x}, {self.target_y})..")  

    def assign_random_bush(self, bushes):
        if bushes:
            self.assigned_bush = r.choice(bushes)
            print(f"\033[90m{self.name} assigned to bush at ({round(self.assigned_bush.x)}, {round(self.assigned_bush.y)})\033[0m")
    
    def is_assigned_bush_empty(self):
        if self.assigned_bush is None:
            return True
        return not any(self.assigned_bush.berries)
    
    def update(self, dt, screen_width, screen_height, bushes, prey_list):
        self.rep_cooldown -= dt
        self.rep_cooldown = max(0, self.rep_cooldown)

        self.age += 1 * dt

        if self.resting:
            self.energy += rest_energy_gain * dt
            if self.energy > self.max_energy:
                self.energy = self.max_energy

            self.rest_timer -= dt
            if self.rest_timer <= 0:
                self.resting = False
            return

        self.energy -= passive_energy_loss * dt 
        self.energy = max(0, self.energy) 

        ratio = self.energy / self.max_energy
        shade = int(ratio * 255)
        
        self.colour = (shade, shade, shade)

        if self.energy >= min_rep_energy and self.rep_cooldown <= 0 and self not in awaiting_mate:
            awaiting_mate.append(self)
            print(f"\033[95m{self.name} awaiting mate..\033[0m")

        # Update mate target for all prey currently awaiting a mate
        if self in awaiting_mate:
            others = [p for p in awaiting_mate if p is not self]

            if not others:
                self.waiting_for_mate = True
                self.mate_target = None
                self.mate_timer = reproduction_cooldown
            else:
                self.waiting_for_mate = False
                self.mate_target = min(others, key=lambda p: distance((self.x, self.y), (p.x, p.y)))
                self.target_x = self.mate_target.x
                self.target_y = self.mate_target.y

        if self.waiting_for_mate:
            self.mate_timer -= dt
            if self.mate_timer <= 0:
                # if waiting for mate too long stop
                self.waiting_for_mate = False
                if self in awaiting_mate:
                    awaiting_mate.remove(self)
                    self.rep_cooldown = reproduction_cooldown
                self.mate_target = None
                # optionally pick a new random target to wander
                self.choose_random_target(screen_width, screen_height)

        if self.energy < 30 and self.rest_chance_updated == False:
            self.rest_chance_updated = True
            self.rest_chance -= 1
            
        if self.energy <= 0:
            self.die()
            if not self.is_alive:
                print(f"\033[91m{self.name} has died! (age {int(self.age)})\033[0m")
                death_sfx.play()
            return
    
        # if energy is low, seek assigned bush instead of wandering
        if self.energy < eat_threshold and bushes:
            # assign a random bush if not already assigned, dead, or empty
            if (
                self.assigned_bush is None 
                or self.assigned_bush.dead 
                or self.is_assigned_bush_empty()
            ):
                self.assign_random_bush(bushes)
            
            if self.assigned_bush:
                # aim for the centre of the bush sprite rather than the top-left
                bush_cx = self.assigned_bush.x + BUSH_HALF
                bush_cy = self.assigned_bush.y + BUSH_HALF
                dist_to_bush = distance((self.x, self.y), (bush_cx, bush_cy))
                if dist_to_bush > 1 and (self.target_x, self.target_y) != (bush_cx, bush_cy):
                    self.target_x = bush_cx
                    self.target_y = bush_cy

        if self.mate_target and distance((self.x, self.y), (self.mate_target.x, self.mate_target.y)) < 10:
            partner = self.mate_target

            baby = Prey(self.x, self.y)
            prey_list.append(baby)

            print(f"\033[92m{baby.name} born as an offspring of {self.name} and {partner.name}!\033[0m")
            birth_sfx.play()

            self.energy -= rep_energy_cost
            partner.energy -= rep_energy_cost

            self.resting = True
            self.rest_timer = 10 * dt

            partner.resting = True
            partner.rest_timer = 10 * dt

            self.rep_cooldown = reproduction_cooldown
            partner.rep_cooldown = reproduction_cooldown

            if self in awaiting_mate:
                awaiting_mate.remove(self)
            if partner in awaiting_mate:
                awaiting_mate.remove(partner)

            self.waiting_for_mate = False
            partner.waiting_for_mate = False
            self.mate_target = None
            partner.mate_target = None

        if not (self in awaiting_mate and self.waiting_for_mate):
            # calculate distance to target (pythagoras)
            dx = self.target_x - self.x 
            dy = self.target_y - self.y  
            dist_to_target = (dx**2 + dy**2)**0.5

            if dist_to_target < 2:
                # snap to target
                self.x = self.target_x
                self.y = self.target_y

                # 1/3 chance to rest; 1/2 if energy below 25
                if r.randint(1,self.rest_chance) == 1:
                    self.resting = True
                    self.rest_timer = r.randint(90, 220) / 60.0
                    print(f"\033[94m{self.name} resting for {round(self.rest_timer, 2)} seconds..\033[0m") 

                # pick new target
                self.choose_random_target(screen_width, screen_height)
            else:
                # slowdown as it approaches target
                k = 50  
                step = self.speed * (dist_to_target / (dist_to_target + k))

                self.prev_x = self.x
                self.prev_y = self.y

                self.x += (dx / dist_to_target) * step
                self.y += (dy / dist_to_target) * step

        # eating behaviour - check each frame whenever energy is low
        if self.energy < eat_threshold and self.assigned_bush:
            bush_cx = self.assigned_bush.x + BUSH_HALF
            bush_cy = self.assigned_bush.y + BUSH_HALF
            if distance((self.x, self.y), (bush_cx, bush_cy)) < 10:
                # reset visit timer when we reach the bush
                self.assigned_bush.time_since_visit = 0
                # eat first available berry
                for i, berry in enumerate(self.assigned_bush.berries):
                    if berry:
                        self.assigned_bush.berries[i] = False
                        self.energy_gain = r.randint(energy_gain_lower, energy_gain_higher)
                        self.energy = min(self.max_energy, self.energy + self.energy_gain)
                        print(f"\033[93m{self.name} ate a berry! (+{self.energy_gain} energy)\033[0m")
                        eat_sfx.play()
                        # after eating go wander again
                        self.choose_random_target(screen_width, screen_height)
                        # check if bush is now empty and reassign if needed
                        if self.is_assigned_bush_empty():
                            self.assign_random_bush(bushes)
                        break


    
    def die(self):
        self.speed = 0
        if self.radius > 0:
            self.radius -= 0.1
        else:
            self.is_alive = False

        if self in awaiting_mate:
            awaiting_mate.remove(self)

    def draw(self, surface):
        pg.draw.circle(surface, self.colour, (self.x, self.y), self.radius)