import pygame
from tiles import Tile
from settings import tile_size
from player import Player
from particle import Particle


def read_data(level_map):
    with open(level_map, 'r') as map1:
        return map1.read().splitlines()


class Level:
    def __init__(self, level_data, surface):
        self.level_data = level_data
        self.surface = surface
        self.world_shift = 0
        self.landing = False
        self.taking_off = False
        self.running_right = False
        self.running_left = False
        self.on_ground = False
        self.particles = pygame.sprite.Group()
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
        self.previous_direction = self.player.sprite.direction.y
        collision_tolerance = 30
        self.on_ground = False
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            if tile.rect.bottom - self.player.sprite.rect.top < collision_tolerance:
                self.player.sprite.rect.top = tile.rect.bottom
                self.player.sprite.direction.y = 0
            elif self.player.sprite.direction.y > 0 and self.player.sprite.rect.bottom - tile.rect.top < collision_tolerance:
                self.player.sprite.rect.bottom = tile.rect.top
                self.player.sprite.direction.y = 0
                self.on_ground = True
                self.player.sprite.jump()

    def check_state(self):
        player = self.player.sprite
        if player.direction.x == 0 and self.on_ground:
            player.state = "idle"
        elif player.direction.y <= 1 and player.direction.x != 0 and player.direction.y >= 0:
            player.state = "run"
        elif player.direction.y > 1 or player.direction.y < 0:
            player.state = "jump"
        print(player.state, player.direction.x, player.direction.y, player.rect.y, self.on_ground)

    def particle_state(self):
        if self.on_ground and self.player.sprite.direction.y < 0:
            self.taking_off = True
            particle_offset = pygame.math.Vector2(-10, 30)
            jump_particle = Particle(self.player.sprite.rect.bottomleft - particle_offset)
            jump_particle.state = 'jump'
            self.particles.add(jump_particle)
        elif self.previous_direction > 1.5 and self.on_ground:
            self.landing = True
            particle_offset = pygame.math.Vector2(20, 40)
            landing_particle = Particle(self.player.sprite.rect.bottomleft - particle_offset)
            landing_particle.state = 'land'
            self.particles.add(landing_particle)
        else:
            self.taking_off, self.landing = False, False
        if self.taking_off or self.landing:
            print(f"take off={self.taking_off}, landing={self.landing}, {self.previous_direction}, {self.player.sprite.direction.y}")
        player = self.player.sprite
        if player.prev_state != 'run' and player.state == "run":
            if player.moving_right:
                particle_offset = pygame.math.Vector2(10, 0)
                run_particle = Particle(self.player.sprite.rect.bottomleft - particle_offset)
            else:
                particle_offset = pygame.math.Vector2(10, 0)
                run_particle = Particle(self.player.sprite.rect.bottomright - particle_offset, flipped=True)
            run_particle.state = 'run'
            self.particles.add(run_particle)
        for sprite in self.particles.sprites():
            if sprite.state == "run":
                if player.state != 'run':
                    self.particles.remove(sprite)
                else:
                    if player.moving_right:
                        sprite.rect.x, sprite.rect.y = player.rect.x - 10, player.rect.bottom - 10
                    else:
                        sprite.rect.x, sprite.rect.y = player.rect.right - 5, player.rect.bottom - 10
        if player.state == "run":
            # particle_offset = pygame.math.Vector2(10, 15)
            # run_particle = Particle(self.player.sprite.rect.bottomleft - particle_offset)
            # run_particle.state = 'run'
            # self.particles.add(run_particle)
            if player.moving_right:
                self.running_right = True
                self.running_left = False
            else:
                self.running_left = True
                self.running_right = False
        else:
            # self.particles.remove(run_particle)
            self.running_left, self.running_right = False, False
        self.particles.update()
        #print(f"Particle: {self.particles.sprite.rect.x}, {self.particles.sprite.rect.y}, player: {player.rect.x}, {player.rect.y}")
        self.particles.draw(self.surface)
        if self.running_right or self.running_left:
            print(f"run left = {self.running_left}, run right = {self.running_right}")

    def run(self):
        self.tiles.update(self.world_shift)
        self.player.update()
        self.apply_gravity()
        self.collision_x_handler()
        self.collision_y_handler()
        self.check_state()
        self.particle_state()
        self.tiles.draw(self.surface)
        self.player.draw(self.surface)
        self.scroll_x()





