from PIL import Image
import glob
import os
from settings import *

states = ('idle', 'jump', 'run')
new_dir = PLAYER_IMAGES_DIR
files = glob.glob('img/*.png')
os.makedirs(new_dir, exist_ok=True)
# 54*60


def refactor_image(size_x, size_y):
    """
    Function for refactoring sprite images into given sizes.
    We get the image, check if it relates to one of the states,
    crop white borders from it, then resize and rename it.
    :param size_x:
    :param size_y:
    :return:
    """
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

