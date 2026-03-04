import settings as set
import pygame as pg
import random as r
from system.distance import distance

pg.mixer.init()

# mating queue for predators
predator_awaiting_mate = []

class Predator:
    counter = 0
    def __init__(self, x, y):
        self.name = f"Predator{Predator.counter}"
        Predator.counter += 1

        self.x = x
        self.y = y

        self.speed = 2.5
        self.colour = None
        self.radius = set.predator_radius
        self.age = 0
        self.detection_radius = set.pred_detect_radius

        self.nearest_prey = None
        self.min_dist = 0
        self.catch_radius = 15
        self.hunt_cooldown = 10

        self.max_energy = 150
        self.energy = 100
        self.energy_gain = set.pred_energy_gain
        self.eat_timer = set.pred_eat_timer
        self.is_alive = True
        self.passive_energy_loss = 3.5
        self.eat_threshold = set.pred_eat_threshold

        self.rep_cooldown = set.pred_rep_cooldown
        self.waiting_for_mate = False
        self.mate_target = None
        self.mate_timer = 15

        self.target_x = r.randint(0, set.screen_width)
        self.target_y = r.randint(0, set.screen_height)
        self.current_target = None

    def pred_wander(self):
        self.target_x = r.randint(0, set.screen_width)
        self.target_y = r.randint(0, set.screen_height)

    def update(self, prey_list, pred_list, dt):
        self.age += 1* dt

        if self.energy <= 0:
            self.die()
            if not self.is_alive:
                print(f"{self.name} has died at age {self.age}!")
            return
        
        # if the prey it was targeting was eaten by someone else, stop freezing
        if self.current_target is not None and self.current_target not in prey_list:
            self.current_target = None
            self.speed = 2.5
            self.eat_timer = set.pred_eat_timer

        # if the prey it was eating runs away, stop freezing and resume
        if self.current_target is not None:
            try:
                d_curr = distance((self.x, self.y), (self.current_target.x, self.current_target.y))
            except Exception:
                d_curr = None
            if d_curr is None or d_curr >= self.catch_radius:
                try:
                    self.current_target.speed = 2
                except Exception:
                    pass
                self.current_target = None
                self.speed = 2.5
                self.eat_timer = set.pred_eat_timer

        # cooldown tick for reproduction
        self.rep_cooldown -= dt
        if self.rep_cooldown < 0:
            self.rep_cooldown = 0

        self.energy -= self.passive_energy_loss * dt 
        self.energy = max(0, self.energy) 

        ratio = self.energy / self.max_energy
        shade = int(ratio * 255)
        
        self.colour = (shade, 0, 0)
        self.hunt_cooldown -= r.randint(2,6) * dt

        # reproduction logic (similar to Prey)
        # enter mating queue when energy high and cooldown finished
        if self.energy >= set.pred_min_rep_energy and self.rep_cooldown <= 0 and self not in predator_awaiting_mate:
            predator_awaiting_mate.append(self)
        # update mate targets for those in queue
        if self in predator_awaiting_mate:
            others = [p for p in predator_awaiting_mate if p is not self]
            if not others:
                self.waiting_for_mate = True
                self.mate_target = None
                self.mate_timer = set.pred_rep_cooldown
            else:
                self.waiting_for_mate = False
                self.mate_target = min(others, key=lambda p: distance((self.x, self.y), (p.x, p.y)))
                self.target_x = self.mate_target.x
                self.target_y = self.mate_target.y
        if self.waiting_for_mate:
            self.mate_timer -= dt
            if self.mate_timer <= 0:
                self.waiting_for_mate = False
                if self in predator_awaiting_mate:
                    predator_awaiting_mate.remove(self)
                    self.rep_cooldown = set.pred_rep_cooldown
                self.mate_target = None
                self.pred_wander()

        target_prey = self.detect_prey(prey_list)
        # handle mating if close to mate target
        if self.mate_target and distance((self.x, self.y), (self.mate_target.x, self.mate_target.y)) < 10:
            partner = self.mate_target
            baby = Predator(self.x, self.y)
            pred_list.append(baby)
            # energy cost and cooldown
            self.energy -= set.pred_rep_energy_cost
            partner.energy -= set.pred_rep_energy_cost
            self.rep_cooldown = set.pred_rep_cooldown
            partner.rep_cooldown = set.pred_rep_cooldown
            if self in predator_awaiting_mate:
                predator_awaiting_mate.remove(self)
            if partner in predator_awaiting_mate:
                predator_awaiting_mate.remove(partner)
            self.waiting_for_mate = False
            partner.waiting_for_mate = False
            self.mate_target = None
            partner.mate_target = None
        
        if target_prey is not None and self.hunt_cooldown <= 0 and self.energy < self.eat_threshold:
            self.target_x = target_prey.x
            self.target_y = target_prey.y

            if distance((self.x, self.y), (target_prey.x, target_prey.y)) < self.catch_radius:
                self.eat_timer -= 1 * dt

                if self.eat_timer <= 0:
                    prey_list.remove(target_prey)
                    if self.current_target and self.current_target in prey_list:
                        self.current_target.speed = 2
                    self.current_target = None
                    print(f"\033[38;5;208m{target_prey.name} has been hunted by {self.name}!")
                    target_prey.is_alive = False
                    target_prey.x = -1000
                    target_prey.y = -1000
                    
                    self.energy = min(self.max_energy, self.energy + self.energy_gain)
                    self.speed = 2.5
                    self.pred_wander()
                    self.eat_timer = set.pred_eat_timer
                else:
                    # freeze only the prey we're currently eating
                    if self.current_target is not None and self.current_target is not target_prey:
                        # restore previous target if switching
                        try:
                            self.current_target.speed = 2
                        except Exception:
                            pass
                    if self.current_target is None:
                        self.current_target = target_prey
                    self.speed = 0
                    self.current_target.speed = 0

        # Always move toward target
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

    def detect_prey(self, prey_list):
        nearest = None
        min_dist = self.detection_radius

        for p in prey_list:
            d = distance((self.x, self.y), (p.x, p.y))
            if d < min_dist:
                min_dist = d
                nearest = p
        return nearest

    def die(self):
        self.speed = 0
        if self.radius > 0:
            self.radius -= 0.1
        else:
            self.is_alive = False

        if self in predator_awaiting_mate:
            predator_awaiting_mate.remove(self)

    def draw(self, surface):
        pg.draw.circle(surface, self.colour, (self.x, self.y), self.radius)