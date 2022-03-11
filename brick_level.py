import pygame
import os
from settings import *


class LevelBrick(pygame.sprite.Sprite):
    def __init__(self, name, pos, level, *, activate=True, completed=False, for_activation=None):
        super().__init__()
        self.name = name
        _path = self.name + "_mod.png"
        self.image = pygame.image.load(os.path.join(BLOCK_DIR, _path)).convert_alpha()
        self.check_sign = pygame.image.load(CHECK_DIR).convert_alpha()
        self.loaded = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.level = level
        self.activate = activate
        self.completed = completed
        self.for_activation = for_activation

    def is_completed(self,):
        if self.completed:
            check = self.check_sign
            self.image.blit(check, (10, 40))

    def is_activated(self):
        if not self.activate:
            tint_surf = self.image.copy()
            tint_surf.fill("black", None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))
        else:
            self.image.blit(self.loaded, (0, 0))

    def update(self):
        self.is_activated()
        self.is_completed()
