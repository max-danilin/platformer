import pygame
import sys
from settings import *
from overworld import Overworld
from player import Player


class Platformer:
    """
    Main class for the game with main loop
    """
    def __init__(self):
        """
        Initializing pygame, creating player and overworld
        """
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        pygame.mixer.init()

        self.player = Player((0, 0))
        self.overworld = Overworld(self.screen, self.player)

        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).set_volume(0.05)

    @staticmethod
    def process_events():
        """
        Process occuring events and return them
        :return:
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        return events

    def run(self):
        """
        Main game function
        :return:
        """
        while True:
            events = self.process_events()

            self.screen.fill('grey')
            self.overworld.run(events)

            pygame.display.update()
            self.clock.tick(60)


game = Platformer()
game.run()
