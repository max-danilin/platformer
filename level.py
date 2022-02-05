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
        self.gravity = -4
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
            self.world_shift = 1
            player.speed.x = 0
        elif player_x > 1000 and direction_x > 0:
            self.world_shift = -1
            player.speed.x = 0
        else:
            self.world_shift = 0
            player.speed.x = 5

    def apply_gravity(self):
        player = self.player.sprite
        player.gravity = self.gravity
        #player.direction.y = 1

    def collision_x_handler(self):
        collision_tolerance = 10
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            #print(self.player.sprite.rect.left, tile.rect.right)
            if self.player.sprite.direction.x < 0 and tile.rect.right - self.player.sprite.rect.left < collision_tolerance and (
                    tile.rect.bottom - self.player.sprite.rect.top > collision_tolerance and self.player.sprite.rect.bottom - tile.rect.top > collision_tolerance
            ):
                self.player.sprite.rect.left = tile.rect.right
                #print("")
                #print(f"top tile {tile.rect.top} bot player {self.player.sprite.rect.bottom} bot tile {tile.rect.bottom} top player {self.player.sprite.rect.top}")
            elif self.player.sprite.direction.x > 0 and self.player.sprite.rect.right - tile.rect.left < collision_tolerance and (
                    tile.rect.bottom - self.player.sprite.rect.top > collision_tolerance and self.player.sprite.rect.bottom - tile.rect.top > collision_tolerance
            ):
                self.player.sprite.rect.right = tile.rect.left

    def collision_y_handler(self):
        collision_tolerance = 15
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            if self.player.sprite.rect.left < tile.rect.right and self.player.sprite.rect.right > tile.rect.left and tile.rect.bottom - self.player.sprite.rect.top < collision_tolerance:
                self.player.sprite.rect.top = tile.rect.bottom
            elif self.player.sprite.direction.y > 0 and self.player.sprite.rect.bottom - tile.rect.top < collision_tolerance:
                self.player.sprite.rect.bottom = tile.rect.top
                self.player.sprite.direction.y = 0
                self.player.sprite.jump()

    def check_standing(self):
        collision_tolerance = 10
        for tile in self.tiles.sprites():
            if self.player.sprite.rect.left < tile.rect.right and self.player.sprite.rect.right > tile.rect.left and (
                    self.player.sprite.rect.bottom - tile.rect.top < collision_tolerance):
                print("------------------")
                return True

    def run(self):
        self.tiles.update(self.world_shift)
        self.player.update()
        self.apply_gravity()
        self.collision_x_handler()
        self.collision_y_handler()

        # if self.check_standing():
        #     self.player.sprite.jump()

        self.tiles.draw(self.surface)
        self.player.draw(self.surface)
        self.scroll_x()




