import pygame
from tiles import Tile
from settings import tile_size, RIGHT_SCREEN_EDGE, LEFT_SCREEN_EDGE
from player import Player
from particle import Particle
import logging

log = logging.getLogger("platform")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(module)s - %(levelname)s - %(message)s'))
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.DEBUG)

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
        self.gravity = 0.5
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
        """
        Scroll the whole level if player reaches certain positions
        :return:
        """
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        player.shift_speed = player.speed.x

        if player_x < LEFT_SCREEN_EDGE and direction_x < 0:
            self.world_shift = player.shift_speed
            player.speed.x = 0
        elif player_x > RIGHT_SCREEN_EDGE and direction_x > 0:
            self.world_shift = -player.shift_speed
            player.speed.x = 0
        else:
            self.world_shift = 0

    def apply_gravity(self):
        """
        Applying gravity onto player object
        :return: None
        """
        player = self.player.sprite
        player.direction.y += self.gravity

    def permit_jump(self):
        """

        :return:
        """
        player = self.player.sprite
        if self.on_ground:
            player.jump()

    def collision_x_handler(self):
        collision_tolerance = 10
        for tile in pygame.sprite.spritecollide(self.player.sprite, self.tiles.sprites(), 0):
            if tile.rect.right - self.player.sprite.rect.left < collision_tolerance:
                self.player.sprite.rect.left = tile.rect.right
                log.debug(f"top tile {tile.rect.top} bot player {self.player.sprite.rect.bottom} bot tile {tile.rect.bottom} top player {self.player.sprite.rect.top}")
            elif self.player.sprite.rect.right - tile.rect.left < collision_tolerance:
                self.player.sprite.rect.right = tile.rect.left
            log.debug(f"COLLIDE {self.player.sprite.rect.left}, {tile.rect.right}")

    def collision_y_handler(self):
        self.previous_direction = self.player.sprite.direction.y
        collision_tolerance = 30
        self.on_ground = False
        player = self.player.sprite
        saving_position = player.rect.y
        collided_y = False
        log.info(f"Player y = { player.rect.y}, exact y = {self.player.sprite.exact_y}")
        player.rect.y = self.player.sprite.exact_y
        #print(player.state, player.direction.x, player.direction.y, player.rect.y, self.on_ground)
        for tile in pygame.sprite.spritecollide(player, self.tiles.sprites(), 0):
            collided_y = True
            log.debug("COLLISION Y")
            if tile.rect.bottom - player.rect.top < collision_tolerance:
                player.rect.top = tile.rect.bottom
                player.direction.y = 0
            elif player.direction.y > 0:
            #elif player.direction.y > 0 and player.rect.bottom - tile.rect.top < collision_tolerance:
                player.rect.bottom = tile.rect.top
                player.direction.y = 0
                self.on_ground = True
                #player.jump()
        player.rect.y = saving_position if not collided_y else player.rect.y

    def check_state(self):
        player = self.player.sprite
        if player.direction.x == 0 and self.on_ground:
            player.state = "idle"
        elif player.direction.x != 0 and self.on_ground:
        #elif player.direction.y <= 1 and player.direction.x != 0 and player.direction.y >= 0:
            player.state = "run"
        elif player.direction.y > 1 or player.direction.y < 0:  # TODO Redo this expression, prob with just else
            player.state = "jump"
        log.info(f"State = {player.state}, direction x = {player.direction.x}, direction y = {player.direction.y}, rect y = {player.rect.y}, on ground = {self.on_ground}")

    def particle_state(self):  # TODO Simplify function
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
        # if self.taking_off or self.landing:
        #     print(f"take off={self.taking_off}, landing={self.landing}, {self.previous_direction}, {self.player.sprite.direction.y}")
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
                        sprite.flipped = False
                    else:
                        sprite.rect.x, sprite.rect.y = player.rect.right - 5, player.rect.bottom - 10
                        sprite.flipped = True
        if player.state == "run":
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
        # if self.running_right or self.running_left:
        #     print(f"run left = {self.running_left}, run right = {self.running_right}")

    def run(self):
        """
        Running level following these consecutive steps:
        0. Create tiles and other non-player objects
        1. Get changes to player state according to inputs and external level effects(such as gravity)
        2. Change player's position
        3. Process new positions into level internal state(such as collision detection)
        4. Get player's new state according to new circumstances
        5. Draw everything
        :return:
        """

        # 1.
        self.apply_gravity()
        self.permit_jump()

        # 2.
        self.player.update()
        self.tiles.update(self.world_shift)

        # 3.
        self.collision_x_handler()
        self.collision_y_handler()
        self.scroll_x()

        # 4.
        self.check_state()
        self.particle_state()
        log.info("-------------")

        # 5.
        self.tiles.draw(self.surface)
        self.player.draw(self.surface)






