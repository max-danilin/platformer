import pygame
import os
from settings import *
from level import Level


class LevelBrick(pygame.sprite.Sprite):
    """
    Class for creating levels, represented by bricks, in overworld.
    """
    def __init__(self, name, pos, level, *, activate=True, completed=False, for_activation=None):
        """
        active - copy of initial image to use when level becomes active
        inactive - image for inactive levels
        :param name: name of the level
        :param pos: position of the brick
        :param level: level map to load
        :param activate: whether level was activated
        :param completed: whether level was completed
        :param for_activation: levels you need to complete to activate certain level
        """
        super().__init__()
        self.level = level
        self.activate = activate
        self.completed = completed
        self.for_activation = for_activation
        self.name = name
        self.created_level = False
        self.associated_level = None
        self.stop_level = False

        # Images
        _path = self.name + "_mod.png"
        self.image = pygame.image.load(os.path.join(BLOCK_DIR, _path)).convert_alpha()
        self.check_sign = pygame.image.load(CHECK_DIR).convert_alpha()

        # Active levels or not
        self.active = self.image.copy()
        self.inactive = self.image.copy()
        self.inactive.fill("black", None, pygame.BLEND_RGBA_MULT)
        self.is_activated()

        self.rect = self.image.get_rect(topleft=pos)

    def create_level(self, surface, player, ui):
        self.associated_level = Level(level_bricks[self.name]['level'], surface, player, ui)

    def run_level(self, surface, player, ui):
        if not self.created_level:
            self.create_level(surface, player, ui)
            self.created_level = True
        self.associated_level.run()
        if self.associated_level.completed:
            self.completed = True
            self.stop_level = True
        elif self.associated_level.back_to_menu:
            self.stop_level = True
            self.associated_level.back_to_menu = False
        else:
            self.stop_level = False

    def is_completed(self):
        """
        Function to determine whether to draw check sign on a level
        :return:
        """
        if self.completed:
            check = self.check_sign
            self.image.blit(check, (10, 40))

    def is_activated(self):
        """
        Function to check whether level was activated
        :return:
        """
        self.image = self.inactive if not self.activate else self.active

    def update(self):
        self.is_completed()
