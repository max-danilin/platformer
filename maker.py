from PIL import Image, UnidentifiedImageError
import glob
import os
from settings import *

#states = ('idle', 'jump', 'run')
#new_dir = PLAYER_IMAGES_DIR
#new_dir = "collect_new"
#new_dir = "new blocks"
#files = os.listdir("block levels")
#files = glob.glob('img/*.png')
#files = os.listdir('Collectable Object/')
#os.makedirs(new_dir, exist_ok=True)
# 54*60


def refactor_image(size_x, size_y, files, states, new_dir):
    """
    Function for refactoring sprite images into given sizes.
    We get the image, check if it relates to one of the states,
    crop white borders from it, then resize and rename it.
    :param new_dir: destination folder
    :param states: sequence of states
    :param files: source files as list
    :param size_x:
    :param size_y:
    :return:
    """
    if 0 < size_y < 1000 and 0 < size_x < 1000:
        pass
    else:
        raise ValueError(f"Sizes should be in range 1-1000, not {size_y} and {size_x}")
    if isinstance(files, list) or isinstance(files, tuple):
        pass
    else:
        raise TypeError("Files should be list or tuple.")
    if isinstance(states, list) or isinstance(states, tuple):
        pass
    else:
        raise TypeError("States should be list or tuple.")
    try:
        os.makedirs(new_dir, exist_ok=True)
    except TypeError:
        raise TypeError('New dir should be string.')
    for file in files:
        for state in states:
            if file.lower().find(state) != -1:
                try:
                    im = Image.open(file)
                except UnidentifiedImageError:
                    raise TypeError(f"Wrong image format {file[file.find('.'):]}")
                f_name = os.path.split(file)[1]
                name = f_name[:-4] + "_mod.png"
                im.getbbox()
                im = im.crop(im.getbbox())
                im = im.resize((size_x, size_y))
                path = os.path.join(new_dir, name)
                im.save(path)


def refactor_tile_image(size_x, size_y, files, new_dir):
    """
    Function for refactoring sprite images into given sizes.
    We get the image, check if it relates to one of the states,
    crop white borders from it, then resize and rename it.
    :param size_x:
    :param size_y:
    :return:
    """
    for file in files:
        im = Image.open(os.path.join("block levels", file))
        name = file[:-4] + "_mod.png"
        print(file, name)
        # im.getbbox()
        # im = im.crop(im.getbbox())
        im = im.resize((size_x, size_y))
        new_path = os.path.join(new_dir, name)
        im.save(new_path)

#refactor_tile_image(48, 48)

# new_dir = "graphics/collect_new"
# files = os.listdir('graphics/collect_new/coins')
# os.makedirs(new_dir, exist_ok=True)
#
# for file in files:
#     im = Image.open(os.path.join("graphics/collect_new/coins", file))
#     name = file[:-4] + "_mod.png"
#     im = im.resize((24, 24))
#     path = os.path.join(new_dir, name)
#     im.save(path)

#refactor_tile_image(192, 178)
#refactor_image(0, 1, glob.glob("img"), ('run',), 123)