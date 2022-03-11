import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from player import Player


class Platformer:
    """
    Main class for the game with main loop
    """
    def __init__(self):
        """
        Initializing pygame
        running_level - checks if any level is currently running
        levels_dict: dictionary with all created levels
        overworld: created overworld class
        """
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.player = Player((0, 0))
        self.levels_dict = {level: Level(level_bricks[level]['level'], self.screen, self.player) for level in level_bricks}
        self.overworld = Overworld(self.screen, self.player)

        self.running_level = False

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('grey')
            if self.overworld.proceed_to_level and not self.running_level:
                brick_level = self.overworld.proceed_to_level
                self.running_level = True
                self.overworld.proceed_to_level = None
            elif not self.overworld.proceed_to_level and not self.running_level:
                self.overworld.run()
            else:
                self.overworld.running = False
                level = self.levels_dict[brick_level.name]
                level.run()
                if level.completed:
                    brick_level.completed = True
                    brick_level.is_completed()
                    self.running_level = False
                    self.player.rect.center = brick_level.rect.center
                elif level.back_to_menu:
                    self.running_level = False
                    level.back_to_menu = False
                    self.player.rect.center = brick_level.rect.center

            pygame.display.update()
            self.clock.tick(60)


game = Platformer()
game.run()