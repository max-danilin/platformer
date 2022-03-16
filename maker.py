from PIL import Image
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
    :param size_x:
    :param size_y:
    :return:
    """
    os.makedirs(new_dir, exist_ok=True)
    for file in files:
        for state in states:
            if file.lower().find(state) != -1:
                im = Image.open(file)
                name = file[4:-4] + "_mod.png"
                im.getbbox()
                im = im.crop(im.getbbox())
                im = im.resize((size_x, size_y))
                path = os.path.join(new_dir, name)
                im.save(path)


def refactor_tile_image(size_x, size_y):
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