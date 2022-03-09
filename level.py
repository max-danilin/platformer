import pygame
from tiles import Tile, StaticTile, EnemyTile, ObjectTile, CollisionTreeTile, CoinTile, TerrainTile
from settings import *
from player import Player
from particle import Particle
import logging
import utils
import sys
from decoration import Sky, Water, Clouds

log = logging.getLogger("platform")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(module)s - %(levelname)s - %(message)s'))
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)


class Level: # TODO Investigate lags
    """
    Class for creating, adjusting and processing level of the game.
    """
    def __init__(self, level_data, surface):
        """
        world_shift - allows us to move camera when player reaches certain lines on the screen
        on_ground - checks whether player is on the ground
        :param level_data: level map in txt format
        :param surface: surface to draw on
        """
        self.level_data = level_data
        self.surface = surface

        self.world_shift = 0
        self.on_ground = False
        self.gravity = 0.5
        self.level_width = 0
        self.completed = False

        self.particles = pygame.sprite.Group()

        self.terrain_tiles = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.enemy_tiles = pygame.sprite.Group()
        self.objects_tiles = pygame.sprite.Group()
        self.constrains = pygame.sprite.Group()
        self.level_end = pygame.sprite.Group()

        self.players = pygame.sprite.GroupSingle()

        for key in self.level_data:
            self.create_tile_group(key)

        self.all_tiles = [self.background_tiles, self.terrain_tiles, self.enemy_tiles, self.objects_tiles]

        self.sky = Sky(8)
        self.water = Water(screen_height - 40, self.level_width)
        self.clouds = Clouds(400, self.level_width, 20)

    def create_tile_group(self, type):
        """
        Method for creating tile groups for terrain, trees, enemies ans so son
        :param type: type of tiles to create
        :return:
        """
        tilefile = utils.import_csv(self.level_data[type])
        row = 0
        for line in tilefile:
            if not self.level_width:
                self.level_width = len(line) * tile_size
            for column, item in enumerate(line):
                if item != '-1':
                    x = tile_size * column
                    y = tile_size * row
                    if type == 'terrain':
                        terrain_tile_list = utils.import_tileset('graphics/tiles_new/Tileset_mod.png')
                        terrain_surf = terrain_tile_list[int(item)]
                        sprite = TerrainTile(tile_size, (x, y), terrain_surf)
                        self.terrain_tiles.add(sprite)
                    if type in ('enemies', 'constrains'):
                        enemies_tile_list = utils.import_tileset('graphics/enemy/setup_tile.png')
                        enemies_surf = enemies_tile_list[int(item)]
                        if item == '0':
                            sprite = EnemyTile(tile_size, (x, y), enemies_surf)
                            self.enemy_tiles.add(sprite)
                        elif item == '1':
                            sprite = Tile(tile_size, (x, y))
                            self.constrains.add(sprite)
                    if type == 'player':
                        player_tile_list = utils.import_tileset('graphics/setup_tiles.png')
                        if item == '0':
                            player = Player((x, y))
                            self.players.add(player)
                        elif item == '1':
                            sprite = Tile(tile_size, (x,y))
                            self.level_end.add(sprite)
                    if type == 'grass':
                        img = pygame.image.load(grass_tiles[int(item)]).convert_alpha()
                        sprite = StaticTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type == 'trees':
                        img = pygame.image.load(tree_tiles[int(item)]).convert_alpha()
                        sprite = StaticTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type == 'fg trees':
                        img = pygame.image.load(fg_trees[int(item)]).convert_alpha()
                        sprite = CollisionTreeTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type == 'coins':
                        img = pygame.image.load(coin_tiles[int(item)]).convert_alpha()
                        if item == '0':
                            sprite = CoinTile(tile_size, (x, y), img)
                        else:
                            sprite = ObjectTile(tile_size, (x, y), img)
                            if item == '1':
                                sprite.value = 5
                            elif item == '3':
                                sprite.value = 10
                            elif item == '2':
                                sprite.hp_recovery = True
                        self.objects_tiles.add(sprite)
            row += 1

    def scroll_x(self, player):
        """
        Scroll the whole level if player reaches certain positions
        We preserve self.player.shift_speed to be able to revert player's speed back to its previous value
        so we can interact with it as it is, instead of dealing with world shift speed.
        :param player: player's sprite
        :return:
        """
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

    def apply_gravity(self, gravity):
        """
        Applying gravity onto player object
        :return: None
        """
        self.players.sprite.direction.y += gravity

    def show_text(self, lives, coins, surface):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 30)
        font_end = pygame.font.SysFont('Arial', 60)
        surf_lives = font.render(f"Player lives = {lives}", True, 'red')
        surf_coins = font.render(f"Player coins = {coins}", True, 'red')
        if self.completed:
            surf_finish = font_end.render(f"Level completed!", True, 'red')
            surface.blit(surf_finish, (300, 300))
        surface.blit(surf_lives, (30, 30))
        surface.blit(surf_coins, (300, 30))

    def permit_jump(self, player):
        """
        Allows player to jump
        :param player: player's sprite
        :return:
        """
        if self.on_ground:
            player.jump()

    def check_defeat(self, player):
        if player.rect.y > screen_height or player.lives <= 0:
            pygame.quit()
            sys.exit()

    def objects_collision(self, player, objects):
        for object in pygame.sprite.spritecollide(player, objects, dokill=True):
            player.coins += object.value
            if object.hp_recovery:
                player.lives += 1

    def enemy_collision(self, player, enemies):
        if pygame.sprite.spritecollide(player, enemies, dokill=False):
            now = pygame.time.get_ticks()
            if now - player.last_hit >= AFTER_DAMAGE_INVUL:
                player.last_hit = now
                player.lives -= 1

    def enemy_constrains(self, enemy, tiles):
        if pygame.sprite.spritecollide(enemy, tiles, dokill=False):
            enemy.enemy_speed *= -1
            enemy.flipped = not enemy.flipped

    def level_finish(self, player, tiles):
        if pygame.sprite.spritecollide(player, tiles, dokill=False):
            self.completed = True

    def collision_x_handler(self, player, tiles):
        """
        Method for handling collisions along X axis
        We use collision tolerance in order to check from which side collision occurs
        and to prevent X collision from happening along Y axis.
        In order to precisely track collision we need to use rounded up values of X and Y
        rather than rounded down 'normal' values. To do so, we assign coordinates to their
        corresponding rounded up values, and then revert it if collision doesn't occur.
        :param tiles: tiles to check collision with
        :param player: player's sprite
        :return:
        """
        saving_position = player.rect.x
        collided_x = False
        player.rect.x = player.exact_x

        collision_tolerance = abs(player.speed.x) + 1
        for tile in pygame.sprite.spritecollide(player, tiles, dokill=False):
            log.info("Collision X")
            collided_x = True
            if tile.rect.right - player.rect.left < collision_tolerance:
                player.rect.left = tile.rect.right
                log.debug(f"COLLIDE X: player left={player.rect.left}, player y={player.rect.y};"
                          f" tile right={tile.rect.right}, tile y={tile.rect.y}")
            elif player.rect.right - tile.rect.left < collision_tolerance:
                player.rect.right = tile.rect.left
                log.debug(f"COLLIDE X: player right={player.rect.right}, player y={player.rect.y};"
                          f" tile left={tile.rect.right}, tile y={tile.rect.y}")
        player.rect.x = saving_position if not collided_x else player.rect.x

    def collision_y_handler(self, player, tiles):
        """
        Method for handling collisions along Y axis (see method for X collisions)
        We use collision tolerance to process collisions happening because of jumping,
        due to gravity all other collisions happen with top of tiles.
        Flag on_ground is set when collision with top of the tile occurs.
        :param tiles: tiles to check collision with
        :param player: player's sprite
        :return:
        """
        collision_tolerance = abs(player.jump_speed) + 1
        self.on_ground = False

        saving_position = player.rect.y
        collided_y = False
        player.rect.y = player.exact_y
        log.debug(f"Player y = {player.rect.y}, exact y = {player.exact_y}")

        for tile in pygame.sprite.spritecollide(player, tiles, dokill=False):
            log.info("Collision Y")
            collided_y = True
            if tile.rect.bottom - player.rect.top < collision_tolerance:
                player.rect.top = tile.rect.bottom
                player.direction.y = 0
                log.debug(f"COLLIDE Y: player x={player.rect.x}, player top={player.rect.top};"
                          f" tile x={tile.rect.x}, tile bottom={tile.rect.bottom}")
            elif player.direction.y > 0:
                player.rect.bottom = tile.rect.top
                player.direction.y = 0
                self.on_ground = True
                log.debug(f"COLLIDE Y: player x={player.rect.x}, player bottom={player.rect.bottom};"
                          f" tile x={tile.rect.x}, tile top={tile.rect.top}")
        player.rect.y = saving_position if not collided_y else player.rect.y

    def check_state(self, player):
        """
        Method for determining player's state for correct animations.
        :param player: player's sprite
        :return:
        """
        if player.direction.x == 0 and self.on_ground:
            player.state = "idle"
        elif player.direction.x != 0 and self.on_ground:
            player.state = "run"
        else:
            player.state = "jump"
        log.info(f"State = {player.state}, direction x = {player.direction.x}, direction y = {player.direction.y},"
                 f" rect y = {player.rect.y}, rect x = {player.rect.x}, on ground = {self.on_ground}")

    def particle_create(self, player):
        """
        Method for creating jump, landing and running particles based on
        player's state and position.
        :param player: player's sprite
        :return:
        """
        if player.prev_state != "jump" and player.direction.y < 0:
            particle_offset = pygame.math.Vector2(-10, 30)
            jump_particle = Particle(player.rect.bottomleft - particle_offset, 'jump')
            self.particles.add(jump_particle)
            log.debug(f"Jump particle created {jump_particle.rect.x}, {jump_particle.rect.y}")
        elif player.prev_state == "jump" and self.on_ground:
            particle_offset = pygame.math.Vector2(20, 40)
            landing_particle = Particle(player.rect.bottomleft - particle_offset, 'land')
            self.particles.add(landing_particle)
            log.debug(f"Landing particle created {landing_particle.rect.x}, {landing_particle.rect.y}")

        if player.prev_state != 'run' and player.state == "run":
            particle_offset = pygame.math.Vector2(10, 0)
            if player.moving_right:
                run_particle = Particle(player.rect.bottomleft - particle_offset, 'run')
            else:
                run_particle = Particle(player.rect.bottomright - particle_offset, 'run', flipped=True)
            self.particles.add(run_particle)
            log.debug(f"Run particle created {run_particle.rect.x}, {run_particle.rect.y}")

    def particle_draw(self, player, particles):
        """
        Method for drawing particles. Run particle should be removed as soon
        as player stops running, jump and landing particles should finish
        their full animations. Offsets are hardcoded for particular particles.
        :param player: player's sprite
        :param particles: group of particles to draw
        :return:
        """
        for sprite in particles.sprites():
            if sprite.state == "run":
                if player.state != 'run':
                    particles.remove(sprite)
                else:
                    if player.moving_right:
                        sprite.rect.x, sprite.rect.y = player.rect.x - 10, player.rect.bottom - 10
                        sprite.flipped = False
                    else:
                        sprite.rect.x, sprite.rect.y = player.rect.right - 5, player.rect.bottom - 10
                        sprite.flipped = True
        particles.update(self.world_shift)
        particles.draw(self.surface)

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

        self.sky.draw(self.surface)
        self.clouds.draw(self.surface, self.world_shift)
        self.water.draw(self.surface, self.world_shift)
        # 1.
        self.apply_gravity(self.gravity)
        self.permit_jump(self.players.sprite)
        self.show_text(self.players.sprite.lives, self.players.sprite.coins, self.surface)

        # 2.
        self.players.update()
        for tile in self.all_tiles:
            tile.update(self.world_shift)
        self.constrains.update(self.world_shift)
        self.level_end.update(self.world_shift)

        # 3.
        self.collision_x_handler(self.players.sprite, self.terrain_tiles)
        self.collision_y_handler(self.players.sprite, self.terrain_tiles)
        self.objects_collision(self.players.sprite, self.objects_tiles)
        self.enemy_collision(self.players.sprite, self.enemy_tiles)
        self.level_finish(self.players.sprite, self.level_end)
        for enemy in self.enemy_tiles.sprites():
            self.enemy_constrains(enemy, self.constrains)
        self.scroll_x(self.players.sprite)

        # 4.
        self.check_defeat(self.players.sprite)
        self.check_state(self.players.sprite)
        self.particle_create(self.players.sprite)
        self.particle_draw(self.players.sprite, self.particles)
        log.info("-------------")

        # 5.
        for tile in self.all_tiles:
            tile.draw(self.surface)
        self.players.draw(self.surface)







