import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from time import perf_counter
from player import Player


pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
player = Player((0, 0))
running_level = False
levels_dict = {level: Level(level_bricks[level]['level'], screen, player) for level in level_bricks}  # TODO Investigate
overworld = Overworld(screen, player)

while True:  # TODO Refactor code
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    if overworld.proceed_to_level and not running_level:
        brick_level = overworld.go_to_level()
        #level = Level(brick_level.level, screen, player)
        running_level = True
        overworld.proceed_to_level = False
    elif not overworld.proceed_to_level and not running_level:
        overworld.run()
    else:
        level = levels_dict[brick_level.name]
        level.run()
        if level.completed:
            brick_level.completed = True
            running_level = False
            player.rect.center = brick_level.rect.center
            overworld.check_level_activation()
        elif level.back_to_menu:
            running_level = False
            level.back_to_menu = False
            player.rect.center = brick_level.rect.center

    pygame.display.update()
    clock.tick(90)
    # fps = clock.get_fps()
    # if 0 < fps < 55:
    #     print(fps, perf_counter())

