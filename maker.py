from PIL import Image
import glob
import os

states = ('idle', 'jump', 'run')
new_dir = "img_new"
files = glob.glob('img/*.png')
os.makedirs(new_dir, exist_ok=True)
# 54*60


def refactor_image(size_x, size_y):
    for file in files:
        for state in states:
            if file.lower().find(state) != -1:
                im = Image.open(file)
                name = file[4:-4] + "_mod.png"
                im.getbbox()
                im2 = im.crop(im.getbbox())
                im3 = im2.resize((size_x, size_y))
                path = os.path.join(new_dir, name)
                im3.save(path)

