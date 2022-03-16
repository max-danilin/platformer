import pygame
from settings import *
from tiles import AnimatedTile, TerrainTile
from random import choice, randint
import glob, os
from utils import get_tile_img


class Sky:
    """
    Class for creating background sky
    """
    def __init__(self, horizon):
        """
        Initializing skies with 3 different images
        :param horizon: line of horizon in rows from top
        """
        self.top = pygame.image.load(os.path.join(SKY_TILES_DIR, 'sky_top.png')).convert()
        self.middle = pygame.image.load(os.path.join(SKY_TILES_DIR, 'sky_middle.png')).convert()
        self.bottom = pygame.image.load(os.path.join(SKY_TILES_DIR, 'sky_bottom.png')).convert()
        self.horizon = horizon

        self.top = pygame.transform.scale(self.top, (screen_width, tile_size))
        self.middle = pygame.transform.scale(self.middle, (screen_width, tile_size))
        self.bottom = pygame.transform.scale(self.bottom, (screen_width, tile_size))

    def draw(self, surface):
        """
        Draw sky depending on Y coordinate
        :param surface:
        :return:
        """
        for row in range(NUM_TILES_Y):
            y = row * tile_size
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))


class Water:
    """
    Class for creating and blitting animated water tiles
    """
    def __init__(self, top, level_width):
        """
        Water tiles, their amount, starting and ending points.
        Creating all the tiles at once.
        imgs - list to save tile images in order not to load them every time
        :param top: Y coordinate for water
        :param level_width:
        """
        water_start = -screen_width
        water_tile_width = WATER_TILE_WIDTH
        tile_x_amount = (level_width + 2 * screen_width) // water_tile_width

        self.water_sprites = pygame.sprite.Group()
        img = pygame.image.load(os.path.join(WATER_TILES_DIR, '1.png')).convert_alpha()
        imgs = get_tile_img(WATER_TILES_DIR)

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(WATER_TILE_WIDTH, (x, y), img)
            sprite.images = imgs
            sprite.animated = True
            self.water_sprites.add(sprite)

    def draw(self, surface, shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)


class Clouds:
    """
    Class for creating cloud tiles in random spots
    """
    def __init__(self, horizon, level_width, cloud_number):
        """
        Creating random clouds in random spaces of the surface, limited by stated boundaries.
        :param horizon: line of the horizon in pixels
        :param level_width:
        :param cloud_number: number of clouds to blit
        """
        cloud_list = [pygame.image.load(cloud).convert_alpha() for cloud in glob.glob(os.path.join(CLOUD_TILE_DIR, '*'))]

        # Boundaries
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon

        self.cloud_sprites = pygame.sprite.Group()

        for _ in range(cloud_number):
            img = choice(cloud_list)
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = TerrainTile(0, (x, y), img)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift):
        self.cloud_sprites.update(shift)
        self.cloud_sprites.draw(surface)
