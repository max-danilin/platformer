import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from player import Player
from ui import UI
from endgame import EndGame
from victory import Victory
from highscore import HighScore


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
        pygame.mixer.init()

        self.player = Player((0, 0))
        self.levels_dict = dict()
        #self.levels_dict = {level: Level(level_bricks[level]['level'], self.screen, self.player) for level in level_bricks}
        self.overworld = Overworld(self.screen, self.player)
        self.ui = UI(self.screen, self.player)
        self.endgame = EndGame(self.screen, self.player)
        self.victory = Victory(self.screen)
        self.highscore = HighScore(self.screen)

        self.running_level = False
        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).set_volume(0.05)

    def run(self):  # TODO Refactor this
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

            self.screen.fill('grey')
            if self.overworld.proceed_to_level and not self.running_level:
                brick_level = self.overworld.proceed_to_level
                self.overworld.proceed_to_level = None
                self.running_level = True
            elif not self.overworld.proceed_to_level and not self.running_level:
                if self.overworld.victory:
                    if self.victory.to_highscore:
                        if not self.highscore.created:
                            self.highscore.add(self.victory.name, self.player.coins, self.player.enemies_killed)
                            self.highscore.load()
                            self.highscore.created = True
                        else:
                            self.highscore.draw()
                    else:
                        self.victory.check_inputs(events)
                        self.victory.draw()
                else:
                    self.overworld.run()
            else:
                if not brick_level.created_level:
                    self.levels_dict[brick_level.name] = Level(
                        level_bricks[brick_level.name]['level'], self.screen, self.player, self.ui
                    )
                    brick_level.created_level = True
                self.overworld.running = False
                level = self.levels_dict[brick_level.name]
                if level.lost:
                    pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).stop()
                    self.endgame.draw()
                else:
                    level.run()
                    if level.completed:
                        brick_level.completed = True
                        brick_level.is_completed()
                        self.running_level = False
                        self.player.levels_completed += 1
                        self.overworld.check_victory()
                    elif level.back_to_menu:
                        self.running_level = False
                        level.back_to_menu = False

            pygame.display.update()
            self.clock.tick(60)


game = Platformer()
game.run()