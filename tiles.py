import pygame
from settings import *
from utils import get_tile_img


def get_images():
    """
    Function to load animated images once for every tile
    :return:
    """
    coin_tile_images = get_tile_img(COINS_DIR)
    enemy_tile_images = get_tile_img(ENEMY_DIR)
    return coin_tile_images, enemy_tile_images


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


class WideTile(pygame.sprite.Sprite):
    """
    Class for creating wide tile
    Used only for combining 2 sprites for processing tree obstacles (for better collision)
    """
    def __init__(self, size, pos):
        """
        :param size: size of a tile
        :param pos: position of a tile
        """
        super().__init__()
        self.image = pygame.Surface((2*size, size))
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
    """
    Class for terrain tiles with image
    """
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img


class StaticTile(Tile):
    """
    Class for static tiles with repositioning
    """
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y+size))


class ObjectTile(StaticTile):
    """
    Class for object tiles
    """
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x + 15, y + size))

        self.value = 0
        self.hp_recovery = False


class AnimatedTile(Tile):
    """
    Class for animated tiles
    """
    def __init__(self, size, pos, img):
        super().__init__(size, pos)
        self.image = img
        self.images = []

        # Animation parameters
        self.animated = False
        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.images):
            self.frame_index = 0
        self.image = self.images[int(self.frame_index)]

    def update(self, x_shift):
        super().update(x_shift)
        if self.animated:
            self.animate()


class CoinTile(AnimatedTile):
    """
    Class for animated coin tiles
    """
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x + 15, y + size))

        self.images = get_images()[0]
        self.image = self.images[0]
        self.animated = True

        self.value = 1
        self.hp_recovery = False


class EnemyTile(AnimatedTile):
    """
    Class for enemy tiles and animation
    We use a bit smaller rect for checking collisions to provide better visuals
    """
    def __init__(self, size, pos, img):
        """
        flipped - preloaded flipped images
        collision_rect - hitbox for collisions with player
        :param size:
        :param pos:
        :param img:
        """
        super().__init__(size, pos, img)
        self.images = get_images()[1]
        self.flipped = [pygame.transform.flip(image, True, False) for image in self.images]
        self.image = self.images[0]
        self.animated = True
        self.enemy_speed = ENEMY_SPEED
        self.flipped_flag = True

        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y + size))
        self.collision_rect = pygame.Rect(
            (self.rect.left+ENEMY_COLLISION_OFFSET, self.rect.top),
            (self.rect.width-ENEMY_COLLISION_OFFSET*2, self.rect.height)
        )

    def update(self, x_shift):
        """
        Update enemy based on its speed and moving direction. Also deal with collision hitbox
        :param x_shift:
        :return:
        """
        super().update(x_shift)
        self.rect.x += self.enemy_speed
        self.collision_rect.y = self.rect.y
        self.collision_rect.x = self.rect.x + ENEMY_COLLISION_OFFSET
        if self.flipped_flag:
            self.image = self.flipped[int(self.frame_index)]


