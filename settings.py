level_map = 'map1'
with open(level_map, 'r') as map1:
    mapping = map1.read().splitlines()

tile_size = 64
screen_width = 1200
screen_height = len(mapping) * tile_size
