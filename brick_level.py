import pygame
from settings import *


class LevelBrick(pygame.sprite.Sprite):
    def __init__(self, pos, level, *, activate=True, completed=False):
        super().__init__()
        self.image = pygame.Surface((LEVEL_BRICK_SIZE, LEVEL_BRICK_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)
        self.level = level
        self.activate = activate
        self.completed = completed
