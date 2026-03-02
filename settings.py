screen_width = 1200
screen_height = 1000

clock_int = 60

background_colour = (49, 110, 0)

stats_size = 24

prey_radius = 5
num_preys = 80
eat_threshold = 80
reproduction_cooldown = 12
rep_energy_cost = 35
min_rep_energy = 70

passive_energy_loss = 1.8
rest_energy_gain = 3

predator_radius = 8
num_preds = 5
pred_rep_cooldown = 25
pred_rep_energy_cost = 75
pred_min_rep_energy = 100

bush_size = 180
num_bushes = 35
energy_gain_lower = 25
energy_gain_higher = 32
berry_regrowth_rate = 6.6
seed_cooldown_lower = 40
seed_cooldown_higher = 60
#seed cooldown (see bush.py __init__)

# time (in seconds) a bush can go without being visited by prey before it withers
bush_abandon_time = 20

famine_enabled = False