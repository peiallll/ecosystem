import pygame as pg
import random as r
from settings import screen_width, screen_height, clock_int, background_colour, num_preys, num_bushes, bush_size, stats_size, famine_enabled, num_preds
from graph import update_plot

from creatures.prey import Prey
from creatures.predator import Predator
from world.bush import Bush

pg.init()
pg.font.init

screen = pg.display.set_mode((screen_width, screen_height))
clock = pg.time.Clock()
running = True
elapsed = 0
times = []
prey_populations = []
bush_populations = []
pred_populations = []
plot_update_counter = 0
sim_time = 0
death_counter = 0

# random time events..
famine_active = False
famine_timer = 0
next_famine_time = r.randint(60, 180)

elapsed_font = pg.font.Font(None, stats_size)

# rmove prey
button_width = 150
button_height = 40
button_x = 20
button_y = 60
button_rect = pg.Rect(button_x, button_y, button_width, button_height)
button_font = pg.font.Font(None, 24)

p = Prey(screen_width / 2, screen_height / 2)
x = Predator(screen_width / 2, screen_height / 2)

prey_pop_font = pg.font.Font(None, stats_size)
bush_pop_font = pg.font.Font(None, stats_size)
fps_font = pg.font.Font(None, stats_size)
death_count_font = pg.font.Font(None, stats_size)

prey_list = []
for prey in range(num_preys):
    x = r.randint(0, screen_width)
    y = r.randint(0, screen_height)
    prey_list.append(Prey(x,y))

pred_list = []
for pred in range(num_preds):
    x = r.randint(0, screen_width)
    y = r.randint(0, screen_height)
    pred_list.append(Predator(x,y))

bush_list = []
for bush in range(num_bushes):
    x = r.randint(0, screen_width - bush_size)
    y = r.randint(0, screen_height - bush_size)
    bush_list.append(Bush(x,y))


while running:
    dt = clock.get_time() / 1000
    sim_time += dt

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                prey_list.clear()

    screen.fill(background_colour)

    fps_val = clock.get_fps()
    fps_text = fps_font.render(f"FPS: {int(fps_val)}", True, (200, 200, 200))
    screen.blit(fps_text, (20, 10))

    # Draw button
    pg.draw.rect(screen, (100, 150, 200), button_rect)
    pg.draw.rect(screen, (255, 255, 255), button_rect, 2)
    button_text = button_font.render("Remove All Prey", True, (255, 255, 255))
    screen.blit(button_text, (button_x + 10, button_y + 8))

    elapsed += dt
    times.append(elapsed)

    if famine_active:
        font = pg.font.SysFont(None, 60)
        text = font.render("famine!", True, (255, 0, 0))
        screen.blit(text, (screen_width//2 - text.get_width()//2, 50))

    # remove dead bushes first (visit timer check follows)
    bush_list = [b for b in bush_list if not b.dead]

    # reset each bush's visit timer if any prey is nearby
    for prey in prey_list:
        for bush in bush_list:
            # compute centre of bush for distance
            bush_cx = bush.x + bush_size / 2
            bush_cy = bush.y + bush_size / 2
            dx = prey.x - bush_cx
            dy = prey.y - bush_cy
            if (dx*dx + dy*dy) ** 0.5 < bush_size / 2:
                bush.time_since_visit = 0

    for bush in bush_list:
        bush.update(dt, bush_list)
        bush.draw(screen)

    # remove dead animals and increment death counter
    previous_count = len(prey_list)
    prey_list = [p for p in prey_list if p.is_alive]
    deaths = previous_count - len(prey_list)
    if deaths > 0:
        death_counter += deaths

    for prey in prey_list:
        prey.update(dt, screen_width, screen_height, bush_list, prey_list)
        prey.draw(screen)  

    pred_list = [x for x in pred_list if x.is_alive]
    for pred in pred_list:
        pred.update(prey_list, pred_list, dt)
        pred.draw(screen)

    prey_pop = len(prey_list)
    prey_population = prey_pop_font.render(f"Prey Pop: {prey_pop}", True, (255, 0, 0))
    screen.blit(prey_population, (screen_width - 130, screen_height - 15))

    bush_pop = len(bush_list)
    bush_population = bush_pop_font.render(f"Bush Pop: {bush_pop}", True, (0, 0, 255))
    screen.blit(bush_population, (screen_width - 130, screen_height - 30))

    death_count = death_count_font.render(f"Prey Deaths: {death_counter}", True, (255, 90, 90))
    screen.blit(death_count, (screen_width - 130, screen_height - 45))

    elapsed_surface = elapsed_font.render(f"Time: {round(elapsed,2)}", True, (255, 0, 0))
    screen.blit(elapsed_surface, (screen_width - 130, screen_height - 60))

    prey_populations.append(prey_pop)
    bush_populations.append(len(bush_list))
    pred_populations.append(len(pred_list))

    plot_update_counter += 1

    if plot_update_counter >= 15:
        update_plot(times, prey_populations, bush_populations, pred_populations)
        plot_update_counter = 0


    if not famine_active and sim_time >= next_famine_time and famine_enabled:
        famine_active = True
        famine_timer = r.randint(20,35)
        for x in range(2):
            print("famine! HALF of all bushes are gone")

        bushes_to_remove = r.sample(bush_list, len(bush_list)//2)
        for bush in bushes_to_remove:
            bush_list.remove(bush)

    if famine_active:
        famine_timer -= dt
        if famine_timer <= 0:
            famine_active = False
            next_famine_time = sim_time + r.randint(60,180)

    pg.display.flip()
    clock.tick(clock_int)