import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld


pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
overworld = Overworld(screen)
running_level = False

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    if overworld.proceed_to_level and not running_level:
        level = Level(overworld.go_to_level(), screen)
        running_level = True
        overworld.proceed_to_level = False
    elif not overworld.proceed_to_level and not running_level:
        overworld.run()
    else:
        level.run()
        if level.completed:
            running_level = False

    pygame.display.update()
    clock.tick(60)

