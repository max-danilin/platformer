with open('lvl 0/level 0_terrain.csv', 'r') as map_sample:
    mapping = map_sample.read().splitlines()

tile_size = 64
screen_width = 1200
screen_height = len(mapping) * tile_size
LEVEL_BRICK_SIZE = 50

LEFT_SCREEN_EDGE = screen_width / 5
RIGHT_SCREEN_EDGE = screen_width * 4 / 5

AFTER_DAMAGE_INVUL = 1000
PLAYER_SPEED = 5
ENEMY_SPEED = 1
JUMP_SPEED = -13
ANIMATION_SPEED = 0.15

PLAYER_IMAGES_DIR = "img_new"
PARTICLE_IMAGES_DIR = "dust_particles"
COINS_DIR = "graphics/collect_new/coins"
ENEMY_DIR = "graphics/enemy/run"


# Levels data
level_0 = {
    'terrain': 'lvl 0/level 0_terrain.csv',
    'coins': 'lvl 0/level 0_coins.csv',
    'constrains': 'lvl 0/level 0_constrains.csv',
    'enemies': 'lvl 0/level 0_enemies.csv',
    'player': 'lvl 0/level 0_player.csv',
    'grass': 'lvl 0/level 0_grass.csv',
    'trees': 'lvl 0/level 0_trees.csv',
    'fg trees': 'lvl 0/level 0_fg trees.csv',
    'tree obstacle': "lvl 0/level 0_tree obstacle.csv",
}

levels = [level_0, ]

level_bricks = {
    'level_0': {'name': 'level_0', 'pos': (120, 400), 'level': levels[0], 'activate': True, 'completed': False, 'for_activation': None},
    'level_1': {'name': 'level_1', 'pos': (220, 200), 'level': levels[0], 'activate': True, 'completed': False, 'for_activation': None},
    'level_2': {'name': 'level_2', 'pos': (320, 400), 'level': levels[0], 'activate': False, 'completed': False, 'for_activation': ('level_0', 'level_1')},
    'level_3': {'name': 'level_3', 'pos': (420, 200), 'level': levels[0], 'activate': False, 'completed': False, 'for_activation': ('level_2',)},
}

grass_tiles = {
    0: 'graphics/objects/Grass/1.png',
    1: 'graphics/objects/Grass/2.png',
    2: 'graphics/objects/Grass/3.png',
    3: 'graphics/objects/Grass/4.png',
    4: 'graphics/objects/Grass/5.png',
    5: 'graphics/objects/Grass/6.png',
    6: 'graphics/objects/Grass/7.png',
    7: 'graphics/objects/Grass/8.png',
    8: 'graphics/objects/Grass/9.png',
    9: 'graphics/objects/Grass/10.png',
    10: 'graphics/objects/Bushes/5.png',
    11: 'graphics/objects/Bushes/6.png',
    12: 'graphics/objects/Bushes/7.png',
    13: 'graphics/objects/Bushes/8.png',
    14: 'graphics/objects/Bushes/9.png',
    15: 'graphics/objects/Bushes/1.png',
    16: 'graphics/objects/Bushes/2.png',
    17: 'graphics/objects/Bushes/3.png',
    18: 'graphics/objects/Bushes/4.png',
}

fg_trees = {
    0: 'graphics/objects/Willows/3.png',
    1: 'graphics/objects/Willows/1.png',
    2: 'graphics/objects/Willows/2.png',
}

coin_tiles = {
    0: 'graphics/collect_new/Coin_01_mod.png',
    1: 'graphics/collect_new/Diamond_mod.png',
    2: 'graphics/collect_new/Apple_mod.png',
    3: 'graphics/collect_new/Chest_01_Locked_mod.png',
}

tree_tiles = {
    0: 'graphics/objects/Trees/3.png',
    1: 'graphics/objects/Trees/1.png',
    2: 'graphics/objects/Trees/2.png',
    3: 'graphics/objects/Ridges/6.png',
    4: 'graphics/objects/Ridges/1.png',
    5: 'graphics/objects/Ridges/2.png',
    6: 'graphics/objects/Ridges/3.png',
    7: 'graphics/objects/Ridges/4.png',
    8: 'graphics/objects/Ridges/5.png',
    9: 'graphics/objects/Boxes/6.png',
    10: 'graphics/objects/Boxes/1.png',
    11: 'graphics/objects/Boxes/2.png',
    12: 'graphics/objects/Boxes/3.png',
    13: 'graphics/objects/Boxes/4.png',
    14: 'graphics/objects/Boxes/5.png',
}

