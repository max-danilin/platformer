import pygame
from settings import *
import os


class Tile(pygame.sprite.Sprite):
    """
    Class for creating sprites of tiles
    """
    def __init__(self, size, pos):
        """
        :param size: size of a tile
        :param pos: position of a tile
        """
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('white')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        """
        Method for updating tiles position if camera moves.
        :param x_shift: speed of camera movement
        :return:
        """
        self.rect.x += x_shift


class TerrainTile(Tile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img


class StaticTile(Tile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y+size))


class CollisionTreeTile(StaticTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)


class AnimatedTile(Tile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img
        self.images = []
        self.animated = False
        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED

    def get_img(self, img_dir):
        """
        Method for loading all images for all the states.
        :param img_dir: image directory
        :return:
        """
        for file in os.listdir(img_dir):
            path = os.path.join(img_dir, file)
            img_load = pygame.image.load(path).convert_alpha()
            self.images.append(img_load)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.images):
            self.frame_index = 0
        self.image = self.images[int(self.frame_index)]

    def update(self, x_shift):
        super().update(x_shift)
        if self.animated:
            self.animate()


class ObjectTile(AnimatedTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        self.value = 0
        self.hp_recovery = False
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x+15, y+size))


class CoinTile(AnimatedTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        self.get_img(COINS_DIR)
        self.image = self.images[0]
        self.animated = True
        self.value = 1
        self.hp_recovery = False
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x+15, y+size))


class EnemyTile(AnimatedTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        self.get_img(ENEMY_DIR)
        self.image = self.images[0]
        self.animated = True
        self.enemy_speed = ENEMY_SPEED
        self.flipped = True
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y + size))

    def update(self, x_shift):
        super().update(x_shift)
        self.rect.x += self.enemy_speed
        if self.flipped:
            self.image = pygame.transform.flip(self.image, True, False)

