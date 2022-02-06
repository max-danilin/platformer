import pygame
from tiles import Tile
from settings import tile_size
from player import Player


def read_data(level_map):
    with open(level_map, 'r') as map1:
        return map1.read().splitlines()


class Level:
    def __init__(self, level_data, surface):
        self.level_data = level_data
        self.surface = surface
        self.world_shift = 0
        self.setup()

    def setup(self):
        mapping = read_data(self.level_data)
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        for row, line in enumerate(mapping):
            for column, item in enumerate(line):
                x = tile_size * column
                y = tile_size * row
                if item == '1':
                    tile = Tile(tile_size, (x, y))
                    self.tiles.add(tile)
                elif item == "2":
                    player = Player((x, y))
                    self.player.add(player)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < 200 and direction_x < 0:
            self.world_shift = 5
            player.speed.x = 0
        elif player_x > 1000 and direction_x > 0:
            self.world_shift = -5
            player.speed.x = 0
        else:
            self.world_shift = 0
            player.speed.x = 5

    def apply_gravity(self):
        player = self.player.sprite
        player.direction.y += 0.5

    def collision_x_handler(self):
        collision_tolerance = 10
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            if tile.rect.right - self.player.sprite.rect.left < collision_tolerance:
                self.player.sprite.rect.left = tile.rect.right
                #print(f"top tile {tile.rect.top} bot player {self.player.sprite.rect.bottom} bot tile {tile.rect.bottom} top player {self.player.sprite.rect.top}")
            elif self.player.sprite.rect.right - tile.rect.left < collision_tolerance:
                self.player.sprite.rect.right = tile.rect.left

    def collision_y_handler(self):
        collision_tolerance = 30
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            if tile.rect.bottom - self.player.sprite.rect.top < collision_tolerance:
                self.player.sprite.rect.top = tile.rect.bottom
                self.player.sprite.direction.y = 0
            elif self.player.sprite.direction.y > 0 and self.player.sprite.rect.bottom - tile.rect.top < collision_tolerance:
                self.player.sprite.rect.bottom = tile.rect.top
                self.player.sprite.direction.y = 0
                self.player.sprite.jump()

    def check_state(self):
        player = self.player.sprite
        if player.direction.x == 0 and player.direction.y <= 1 and player.direction.y >= 0:
            player.state = "idle"
        elif player.direction.y <= 1 and player.direction.x != 0 and player.direction.y >= 0:
            player.state = "run"
        elif player.direction.y > 1 or player.direction.y < 0:
            player.state = "jump"
        #print(player.state, player.direction.x, player.direction.y, player.rect.y)

    def run(self):
        self.tiles.update(self.world_shift)
        self.player.update()
        self.apply_gravity()
        self.collision_x_handler()
        self.collision_y_handler()
        self.check_state()
        self.tiles.draw(self.surface)
        self.player.draw(self.surface)
        self.scroll_x()




