level_map = 'map1'
with open(level_map, 'r') as map1:
    mapping = map1.read().splitlines()

tile_size = 64
screen_width = 1200
screen_height = len(mapping) * tile_size

LEFT_SCREEN_EDGE = screen_width / 5
RIGHT_SCREEN_EDGE = screen_width * 4 / 5

PLAYER_SPEED = 5
JUMP_SPEED = -13
ANIMATION_SPEED = 0.15

PLAYER_IMAGES_DIR = "img_new"
PARTICLE_IMAGES_DIR = "dust_particles"
