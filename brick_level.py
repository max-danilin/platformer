import pygame
from settings import *


class LevelBrick(pygame.sprite.Sprite):
    def __init__(self, name, pos, level, *, activate=True, completed=False, for_activation=None):
        super().__init__()
        self.image = pygame.Surface((LEVEL_BRICK_SIZE, LEVEL_BRICK_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)
        self.level = level
        self.name = name
        self.activate = activate
        self.completed = completed
        self.for_activation = for_activation

    def is_completed(self,):
        if self.completed:
            pygame.draw.circle(self.image, 'green', (10, 10), 7)

    def is_activated(self):
        if not self.activate:
            self.image.fill('black')
        else:
            self.image.fill('red')

    def update(self):
        self.is_activated()
        self.is_completed()
