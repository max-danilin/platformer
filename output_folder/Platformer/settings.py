# Position attributes for levels and screen
NUM_TILES_Y = 11
tile_size = 64
screen_width = 1200
screen_height = NUM_TILES_Y * tile_size
LEVEL_BRICK_SIZE = 50
WATER_TILE_WIDTH = 192
ENEMY_COLLISION_OFFSET = 9
LEFT_SCREEN_EDGE = screen_width / 5
RIGHT_SCREEN_EDGE = screen_width * 4 / 5
TREE_OBSTACLE_ADDED_SPACE = 20
GRAVITY = 0.5

# Player's attributes
AFTER_DAMAGE_INVUL = 1000
PLAYER_SPEED = 5
ENEMY_SPEED = 1
JUMP_SPEED = -13
ANIMATION_SPEED = 0.15
BLINKING_DURATION = 30
PLAYER_MAX_LIVES = 5
ALL_STATES = ('idle', "jump", "run")

# UI parameters
HELTH_BAR_POS = (74, 49)
HEALTH_BAR_COLOR = 'red'

# Level images
PLAYER_IMAGES_DIR = "img_new"
PARTICLE_IMAGES_DIR = "dust_particles"
COINS_DIR = "graphics/collect_new/coins"
ENEMY_DIR = "graphics/enemy/run"
BLOCK_DIR = "new blocks"
CHECK_DIR = "graphics/check.png"
TERRAIN_TILESET_DIR = 'graphics/tiles_new/Tileset_mod.png'
ENEMY_TILESET_DIR = 'graphics/enemy/setup_tile.png'

# Background tiles
WATER_TILES_DIR = 'graphics/decoration/water'
SKY_TILES_DIR = 'graphics/decoration/sky'
CLOUD_TILE_DIR = 'graphics/decoration/clouds'

# UI
UI_COIN_DIR = "graphics/ui/coin.png"
UI_HB_DIR = "graphics/ui/health_bar.png"
UI_FONT_DIR = "graphics/ui/ARCADEPI.TTF"

# Musicand sounds
COIN_SOUND_DIR = "audio/effects/coin.wav"
STOMP_SOUND_DIR = "audio/effects/stomp.wav"
HIT_SOUND_DIR = "audio/effects/hit.wav"
JUMP_SOUND_DIR = "audio/effects/jump.wav"
LEVEL_MUSIC_DIR = "audio/level_music.wav"
OVERWORLD_MUSIC_DIR = "audio/overworld_music.wav"
GAMEOVER_SOUND_DIR = "audio/GameOver.wav"

# Hashing
HASH_KEY = "maxd"
HIGHSCORES_DIR = "highscore.dat"

# INITIAL SCREEN
BUTTON_TEXT_COLOR = 'black'
BUTTON_PRESSED_COLOR = '#C71313'
BUTTON_COLOR = '#EF7E7E'
BUTTON_LOWER_COLOR = '#202020'
INITIAL_BACK_DIR = 'graphics/back3.jpg'
BACK_ANIMATION_SPEED = 3
WELCOME_DIR = 'graphics/welcome2.png'
WELCOME_POS = (150, 150)
BUTTON_SIZE = (120, 60)
BUTTON_Y = screen_height - 100
BUTTON_SPACING = 350
BUTTON_ELEVATION = 10
BUTTON_SOUND_TIMEOUT = 30
MUSIC_DIR = 'audio/music.wav'

# NEAT
CONFIG_DIR = 'config.txt'
CONFIG_MULTIPLE_DIR = 'config_multiple.txt'
FOV_DISTANCE = 5
LEFT_FOV_ADJUSTMENT = 2
NEAT_INFO_Y = 30
PLAYER_INACTIVE_LIMIT = 200
FITNESS_LIMIT = -10
NEAT_CHECKPOINT = 5
GENERATION_AMOUNT = 50
WINNER_DIR = 'best.pickle'
DRAW_FLAG = True

CLOCK_RATE = 60
FONT_SIZE = 30
FONT_STD = 'Arial'
BACKGROUND_MUSIC_CHANNEL = 0
OVERWORLD_ESCAPE_TIMEOUT = 2

# Tiles data for levels
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

level_1 = {
    'terrain': 'lvl 1/level 1_terrain.csv',
    'coins': 'lvl 1/level 1_coins.csv',
    'constrains': 'lvl 1/level 1_constrains.csv',
    'enemies': 'lvl 1/level 1_enemies.csv',
    'player': 'lvl 1/level 1_player.csv',
    'grass': 'lvl 1/level 1_grass.csv',
    'trees': 'lvl 1/level 1_trees.csv',
    'fg trees': 'lvl 1/level 1_fg trees.csv',
    'tree obstacle': "lvl 1/level 1_tree obstacle.csv",
}

level_2 = {
    'terrain': 'lvl 2/level 2_terrain.csv',
    'coins': 'lvl 2/level 2_coins.csv',
    'constrains': 'lvl 2/level 2_constrains.csv',
    'enemies': 'lvl 2/level 2_enemies.csv',
    'player': 'lvl 2/level 2_player.csv',
    'grass': 'lvl 2/level 2_grass.csv',
    'trees': 'lvl 2/level 2_trees.csv',
    'fg trees': 'lvl 2/level 2_fg trees.csv',
    'tree obstacle': "lvl 2/level 2_tree obstacle.csv",
}

level_3 = {
    'terrain': 'lvl 3/level 3_terrain.csv',
    'coins': 'lvl 3/level 3_coins.csv',
    'constrains': 'lvl 3/level 3_constrains.csv',
    'enemies': 'lvl 3/level 3_enemies.csv',
    'player': 'lvl 3/level 3_player.csv',
    'grass': 'lvl 3/level 3_grass.csv',
    'trees': 'lvl 3/level 3_trees.csv',
    'fg trees': 'lvl 3/level 3_fg trees.csv',
    'tree obstacle': "lvl 3/level 3_tree obstacle.csv",
}

# Levels list
levels = [level_0, level_1, level_2, level_3, ]

# Brick levels data
level_bricks = {
    'level_0': {
        'name': 'level_0', 'pos': (screen_width/12, screen_height/2), 'level': levels[0], 'activate': True,
        'completed':  False, 'for_activation': None
    },
    'level_1': {
        'name': 'level_1', 'pos': (screen_width/12*3, screen_height/8), 'level': levels[1], 'activate': True,
        'completed':  False, 'for_activation': None
    },
    'level_2': {
        'name': 'level_2', 'pos': (screen_width/12*5, screen_height/2), 'level': levels[2], 'activate': False,
        'completed': False, 'for_activation': ('level_0', 'level_1')
    },
    'level_3': {
        'name': 'level_3', 'pos': (screen_width/12*7, screen_height/8), 'level': levels[3], 'activate': False,
        'completed': False, 'for_activation': ('level_2',)
    },
}

# Tile images
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

