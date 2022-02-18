from csv import reader
import pygame
from settings import *


def import_csv(path):
    #terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            #terrain_map.append(list(row))
            yield row
    #return terrain_map


def import_tileset(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = surface.get_size()[0] // tile_size
    tile_num_y = surface.get_size()[1] // tile_size

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size, tile_size))
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surf)
    return cut_tiles


# m = import_csv(level_0['terrain'])
# for item in m:
#     print(item)