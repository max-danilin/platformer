from csv import reader
import pygame
from settings import *
import os


def import_csv(path):
    """
    Generator function to read csv map files row to row
    :param path: path to csv
    :return: row from file
    """
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            yield row


def import_tileset(path):
    """
    Function for cutting tileset from path to a list with separate images
    :param path: path to look for a tileset
    :return: list of cut tiles from tileset, base on their position in tileset (first row, then column)
    """
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


def get_img(img_dir, states):
    """
    Method for loading all images for all the states.
    :param states: dictionary with states and images
    :param img_dir: image directory
    :return:
    """
    if isinstance(states, dict) or isinstance(states, tuple) or isinstance(states, list):
        pass
    else:
        raise TypeError("States should be dictionary, tuple or list.")
    new_states = dict()
    for state in states:
        new_states[state] = []
        state_path = os.path.join(img_dir, state)
        for file in os.listdir(state_path):
            if file.lower().find(state) != -1:
                path = os.path.join(state_path, file)
                img_load = pygame.image.load(path).convert_alpha()
                new_states[state].append(img_load)
    return new_states


def load_flipped(states):
    """
    Function for pre-generating flipped images to gain additional performance speed
    :param states: dict with states and images
    :return:
    """
    if isinstance(states, dict):
        pass
    else:
        raise TypeError("States should be dictionary.")
    flipped = dict()
    for key, value in states.items():
        flipped[key] = []
        if isinstance(value, list):
            pass
        else:
            raise TypeError("States should contain list as values.")
        for item in value:
            try:
                flip = pygame.transform.flip(item, True, False)
            except TypeError:
                raise TypeError(f"{item} should be surface object, not {type(item)}")
            flipped[key].append(flip)
    return flipped


def get_tile_img(img_dir):
    """
    Method for loading all images for given type of tile.
    :param img_dir: image directory
    :return: list of images from given directory
    """
    images = []
    for file in os.listdir(img_dir):
        path = os.path.join(img_dir, file)
        img_load = pygame.image.load(path).convert_alpha()
        images.append(img_load)
    return images
