import pygame
from settings import *
from tiles import AnimatedTile, TerrainTile
from random import choice, randint
import glob


class Sky:
    def __init__(self, horizon):
        self.top = pygame.image.load('graphics/decoration/sky/sky_top.png').convert()
        self.middle = pygame.image.load('graphics/decoration/sky/sky_middle.png').convert()
        self.bottom = pygame.image.load('graphics/decoration/sky/sky_bottom.png').convert()
        self.horizon = horizon

        self.top = pygame.transform.scale(self.top, (screen_width, tile_size))
        self.middle = pygame.transform.scale(self.middle, (screen_width, tile_size))
        self.bottom = pygame.transform.scale(self.bottom, (screen_width, tile_size))

    def draw(self, surface):
        for row in range(11):
            y = row * tile_size
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))


class Water:
    def __init__(self, top, level_width):
        water_start = -screen_width
        water_tile_width = 192
        tile_x_amount = (level_width + 2 * screen_width) // water_tile_width
        self.water_sprites = pygame.sprite.Group()
        img = pygame.image.load('graphics/decoration/water/1.png').convert_alpha()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(192, (x, y), img)
            sprite.get_img('graphics/decoration/water')
            sprite.animated = True
            self.water_sprites.add(sprite)

    def draw(self, surface, shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)


class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_list = glob.glob('graphics/decoration/clouds/*')
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pygame.sprite.Group()

        for cloud in range(cloud_number):
            cloud = choice(cloud_list)
            img = pygame.image.load(cloud).convert_alpha()
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = TerrainTile(0, (x, y), img)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift):
        self.cloud_sprites.update(shift)
        self.cloud_sprites.draw(surface)
