import pygame
from tiles import Tile, StaticTile, EnemyTile, ObjectTile, CoinTile, TerrainTile, WideTile
from settings import *
from particle import Particle
import logging
import utils
from decoration import Sky, Water, Clouds
from endgame import EndGame
from types import GeneratorType
import numpy


# Logging
log = logging.getLogger("platform")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(module)s - %(levelname)s - %(message)s'))
log.addHandler(stream_handler)
log.setLevel(logging.CRITICAL)  # DEBUG
stream_handler.setLevel(logging.DEBUG)  # INFO


class LevelError(Exception):
    pass


class Level:
    """
    Class for creating, adjusting and processing level of the game.
    """

    def __init__(self, level_data, surface, player, ui):
        """
        world_shift - allows us to move camera when player reaches certain lines on the screen
        on_ground - checks whether player is on the ground
        back_to_menu - flag to check if game should get back to overworld
        postponed - flag to pause level if backspace was hit
        pps - player's position when level was postponed
        ui - player's UI
        endgame- class for endgame screen
        :param level_data: level map in txt format
        :param surface: surface to draw on
        """
        if not isinstance(level_data, dict):
            raise LevelError(f'Level data should be dict, not {type(level_data)}')
        self.level_data = level_data
        self.surface = surface
        self.player = player
        self.ui = ui
        # self.endgame = EndGame(self.surface, self.player)

        # Local level variables
        self.world_shift = 0
        self.gravity = GRAVITY
        self.level_width = 0

        # Flags
        self.on_ground = False
        self.completed = False
        self.back_to_menu = False
        self.postponed = True

        # Particles
        self.particles = pygame.sprite.Group()
        self.run_particles = pygame.sprite.GroupSingle()

        # Tiles
        self.terrain_tiles = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.enemy_tiles = pygame.sprite.Group()
        self.objects_tiles = pygame.sprite.Group()
        self.constrains = pygame.sprite.Group()
        self.level_end = pygame.sprite.Group()
        self.tree_obs = pygame.sprite.Group()

        # Player
        if len(self.player) == 1:
            self.players = pygame.sprite.GroupSingle()
        else:
            self.players = pygame.sprite.Group()

        self.preloaded = Level.preload_images()
        [self.create_tile_group(key) for key in self.level_data]

        # Save player's position
        self.pps = self.save_player(self.players.sprite)

        # Tile group for drawing
        self.all_tiles = [self.background_tiles, self.terrain_tiles, self.enemy_tiles, self.objects_tiles]

        # Background
        self.sky = Sky(8)
        self.water = Water(screen_height - 40, self.level_width)
        self.clouds = Clouds(400, self.level_width, 20)

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 30)

        # Sound
        self.coin_sound = pygame.mixer.Sound(COIN_SOUND_DIR)
        self.coin_sound.set_volume(0.3)
        self.stomp_sound = pygame.mixer.Sound(STOMP_SOUND_DIR)
        self.stomp_sound.set_volume(0.8)
        self.hit_sound = pygame.mixer.Sound(HIT_SOUND_DIR)
        self.level_music = pygame.mixer.Sound(LEVEL_MUSIC_DIR)

        self.keys = {'right': False, 'left': False, 'up': False}
        self.tiles_neat = [self.terrain_tiles, self.enemy_tiles, self.objects_tiles, self.tree_obs]
        self.player_prev_pos = 100
        self.shifted = 0

    @staticmethod
    def load_img(path_dict):
        """
        Loading images from their path's
        :param path_dict: dictionary with paths to images
        :return: dictionary with same key as path_dict and loaded image as value
        """
        if not isinstance(path_dict, dict):
            raise LevelError('Wrong path to dictionary with tiles.')
        img_dict = dict()
        for index, value in path_dict.items():
            img_dict[index] = pygame.image.load(value).convert_alpha()
        return img_dict

    @classmethod
    def preload_images(cls):
        """
        Function for converting type of image into surface with image
        :param type: type of image
        :return:
        """
        preload_dict = {
            'terrain': utils.import_tileset(TERRAIN_TILESET_DIR),
            'enemies': utils.import_tileset(ENEMY_TILESET_DIR),
            'constrains': utils.import_tileset(ENEMY_TILESET_DIR),
            'grass': cls.load_img(grass_tiles),
            'trees': cls.load_img(tree_tiles),
            'fg trees': cls.load_img(fg_trees),
            'coins': cls.load_img(coin_tiles)
        }
        return preload_dict

    def create_tile_group(self, type_):
        """
        Method for creating tile groups for terrain, trees, objects, enemies ans so on
        :param type_: type of tiles to create
        :return:
        """
        if self.level_data.get(type_) is None:
            raise LevelError(f'Tiles of type <{type_}> not found in levels dictionary.')
        tilefile = utils.import_csv(self.level_data[type_])
        if not isinstance(tilefile, GeneratorType):
            raise LevelError('Error during csv import.')
        if type_ not in ('player', "tree obstacle"):
            imgs = self.preloaded[type_]
        row = 0
        for line in tilefile:
            if not isinstance(line, list):
                raise LevelError(f'{line} from {tilefile} should be list.')
            if not self.level_width:
                self.level_width = len(line) * tile_size
            for column, item in enumerate(line):
                if item != '-1':
                    x = tile_size * column
                    y = tile_size * row
                    if type_ == 'terrain':
                        terrain_surf = imgs[int(item)]
                        sprite = TerrainTile(tile_size, (x, y), terrain_surf)
                        self.terrain_tiles.add(sprite)
                    if type_ in ('enemies', 'constrains'):
                        enemies_surf = imgs[int(item)]
                        if item == '0':
                            sprite = EnemyTile(tile_size, (x, y), enemies_surf)
                            self.enemy_tiles.add(sprite)
                        elif item == '1':
                            sprite = Tile(tile_size, (x, y))
                            self.constrains.add(sprite)
                    if type_ == 'player':
                        if item == '0':
                            for player in self.player:
                                player.rect.topleft = (x, y)
                                self.players.add(player)
                        elif item == '1':
                            sprite = Tile(tile_size, (x, y))
                            self.level_end.add(sprite)
                    if type_ == 'grass':
                        img = imgs[int(item)]
                        sprite = StaticTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type_ == 'trees':
                        img = imgs[int(item)]
                        sprite = StaticTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type_ == 'fg trees':
                        img = imgs[int(item)]
                        sprite = StaticTile(tile_size, (x, y), img)
                        self.background_tiles.add(sprite)
                    if type_ == "tree obstacle":
                        sprite = Tile(tile_size + TREE_OBSTACLE_ADDED_SPACE, (x, y))
                        self.tree_obs.add(sprite)
                    if type_ == 'coins':
                        img = imgs[int(item)]
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
        if not isinstance(gravity, int) and not isinstance(gravity, float):
            raise LevelError(f"Gravity should be number, not {type(gravity)}")
        self.players.sprite.direction.y += gravity

    @staticmethod
    def show_text(font, lives, coins, surface):
        """
        !Currently unused!
        Show lives, coins on the surface
        :param font: type of font
        :param lives: player lives
        :param coins: player coins
        :param surface: surface of our game
        :return:
        """
        surf_lives = font.render(f"Player lives = {lives}", True, 'red')
        surf_coins = font.render(f"Player coins = {coins}", True, 'red')
        surface.blit(surf_lives, (30, 30))
        surface.blit(surf_coins, (300, 30))

    def permit_jump(self, player):
        """
        Allows player to jump
        :param player: player's sprite
        :return:
        """
        if self.on_ground:
            player.get_keys(neat=True, keys=self.keys)
            player.jump()
            # player.jump()

    def goto_endscore(self):
        """
        Draws end scene
        :return:
        """
        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).stop()
        self.endgame.draw()

    @staticmethod
    def check_defeat(player):
        """
        Checks if player has fallen or has no lives left
        :param player: player object
        :return:
        """
        if player.rect.y >= screen_height or player.lives <= 0:
            return True

    def tree_collision(self, player, trees):
        """
        Checks collision with invisible tiles inside fg trees (referred as fg tiles further on). Works alike
        collision_y_handler aside of few features.
        First, we process collision if it happens from above with player's direction y > 0 and only in boundaries of
        collided tree object
        Second, if we have collision with 2 fg tiles simultaneously, then they are placed side by side and we group
        them to allow for better collision processing.
        :param player: player's object
        :param trees: invisible tiles with collision inside fg trees
        :return:
        """
        # Usual collision variables, seek reference within collision_handlers
        saving_position = player.rect.y
        collided_y = False
        player.rect.y = player.exact_y
        collision_tolerance = abs(player.direction.y) + 1

        collision = pygame.sprite.spritecollide(player, trees, dokill=False)
        # Grouping 2 tiles into WideTile
        if len(collision) == 2:
            temp = sorted(collision, key=lambda item: item.rect.x)
            collision = [WideTile(tile_size, temp[0].rect.topleft)]
        for tree in collision:
            log.debug(f"Right: {player.rect.right}, {tree.rect.right}, left: {player.rect.left}, {tree.rect.left}, "
                      f"y: {player.rect.bottom}, {tree.rect.top}, direction: {player.direction.y}")
            if player.rect.right < tree.rect.right and player.rect.left > tree.rect.left and player.direction.y > 0 \
                    and player.rect.bottom - tree.rect.top < collision_tolerance:
                collided_y = True
                player.rect.bottom = tree.rect.top
                player.direction.y = 0
                self.on_ground = True
        player.rect.y = saving_position if not collided_y else player.rect.y

    def objects_collision(self, player, objects):
        """
        Process collision with objects, destroy object upon collision, add coins or health to player
        :param player: player's object
        :param objects: objects to collide with
        :return:
        """
        for object_ in pygame.sprite.spritecollide(player, objects, dokill=True):
            player.coins += object_.value
            if object_.value:
                self.coin_sound.play()
            if object_.hp_recovery:
                player.lives += 1

    def add_explosion_particles(self, pos):
        """
        Add explosion particle upon enemy destruction
        :param pos:
        :return:
        """
        particle_offset = pygame.math.Vector2(20, 50)
        self.particles.add(Particle(pos - particle_offset, 'explosion'))

    def enemy_collision(self, player, enemies):
        """
        Method for processing enemy collision. If player hit enemy from above, then enemy is destoyed, and player
        jumps off the enemy. Otherwise player loose 1 life and becomes temporary invulnerable and
        starts blinking for this period of time. Player.blinks set to 0 starts player.blinking.
        killed - flag to let player destroy multiple enemies simultaneously
        :param player: player's object
        :param enemies: enemy tiles
        :return:
        """
        if AFTER_DAMAGE_INVUL < 0:
            raise ValueError("Set proper invulnerability time")
        collision_tolerance = abs(player.direction.y) + 1
        killed = False
        for enemy in enemies:
            if player.rect.colliderect(enemy.collision_rect):
                if player.direction.y > 0 and player.rect.bottom - enemy.collision_rect.top < collision_tolerance:
                    self.add_explosion_particles(enemy.rect.topleft)
                    self.stomp_sound.play()
                    enemies.remove(enemy)
                    player.enemies_killed += 1
                    killed = True
                else:
                    now = pygame.time.get_ticks()
                    if now - player.last_hit >= AFTER_DAMAGE_INVUL:
                        player.last_hit = now
                        self.hit_sound.play()
                        player.lives -= 1
                        player.blinks = 0
        if killed:
            player.direction.y = player.jump_speed

    @staticmethod
    def enemy_constrains(enemy, tiles):
        """
        Checks if enemy collided with invisible constraints, turns enemy if so.
        :param enemy: enemy object
        :param tiles: invisible constraints for enemies
        :return:
        """
        if pygame.sprite.spritecollide(enemy, tiles, dokill=False):
            enemy.enemy_speed *= -1
            enemy.flipped_flag = not enemy.flipped_flag

    def level_finish(self, player, tiles):
        """
        Checks if player collided with level finish tiles
        :param player:
        :param tiles: invisible tiles, marking level's end
        :return:
        """
        if pygame.sprite.spritecollide(player, tiles, dokill=False):
            player.levels_completed += 1
            self.completed = True

    @staticmethod
    def save_player(player):
        """
        Method for saving player's parameters when the level is created and if it is paused
        :param player:
        :return: coordinates, direction and speed in tuples
        """
        rect = player.rect.x, player.rect.y
        direction = player.direction.x, player.direction.y
        speed = player.speed.x, player.speed.y
        return rect, direction, speed

    def return_to_menu(self, player):
        """
        Checks if backspace was hit, then sets flags and saves player
        :param player:
        :return:
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.back_to_menu = True
            self.postponed = True
            self.pps = self.save_player(player)

    def restore_player_neat(self, player):
        """
        Restores player parameters if level is resumed.
        :param player:
        :return:
        """
        if self.postponed:
            # (player.rect.x, player.rect.y), (player.direction.x, player.direction.y), (
            #     player.speed.x, player.speed.y) = self.pps
            self.postponed = False

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

        collision_tolerance = (player.speed.x + 1) * abs(player.direction.x)
        for tile in pygame.sprite.spritecollide(player, tiles, dokill=False):
            log.info("Collision from X")
            if tile.rect.right - player.rect.left < collision_tolerance:
                collided_x = True
                player.rect.left = tile.rect.right
                log.debug(f"COLLIDE X: player left={player.rect.left}, player y={player.rect.y};"
                          f" tile right={tile.rect.right}, tile y={tile.rect.y}")
            elif player.rect.right - tile.rect.left < collision_tolerance:
                collided_x = True
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
            log.info("Collision from Y")
            if tile.rect.bottom - player.rect.top < collision_tolerance:
                collided_y = True
                player.rect.top = tile.rect.bottom
                player.direction.y = 0
                log.debug(f"COLLIDE Y: player x={player.rect.x}, player top={player.rect.top};"
                          f" tile x={tile.rect.x}, tile bottom={tile.rect.bottom}")
            elif player.direction.y > 0:
                collided_y = True
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
            self.run_particles.add(run_particle)
            log.debug(f"Run particle created {run_particle.rect.x}, {run_particle.rect.y}")

    def particle_draw(self, player, particles, run_particles):
        """
        Method for drawing particles. Run particle should be removed as soon
        as player stops running, jump and landing particles should finish
        their full animations. Offsets are hardcoded for particular particles.
        :param run_particles: run particles separately to make calculations faster
        :param player: player's sprite
        :param particles: group of particles to draw
        :return:
        """
        sprite = run_particles.sprite
        if sprite:
            if player.state != 'run':
                run_particles.remove(sprite)
            else:
                if player.moving_right:
                    sprite.rect.x, sprite.rect.y = player.rect.x - 10, player.rect.bottom - 10
                    sprite.flipped_flag = False
                else:
                    sprite.rect.x, sprite.rect.y = player.rect.right - 5, player.rect.bottom - 10
                    sprite.flipped_flag = True
        particles.update(self.world_shift)
        run_particles.update(self.world_shift)
        particles.draw(self.surface)
        run_particles.draw(self.surface)

    def start_music(self):
        """
        Starts background music
        :return:
        """
        if self.postponed:
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).play(self.level_music, loops=-1)

    def fov(self, player):
        # 0 - self.level_width, 0 - screen_height
        pl_x = int((player.rect.x + player.speed.x + 1) // 64)
        pl_y = int(player.rect.y // 64) - 1
        fov_array = numpy.empty(((screen_height // 64) - 1, 5))
        i = 0
        for row in range(pl_x * 64, (pl_x + 5) * 64, 64):
            j = 0
            for column in range(64, screen_height, 64):
                tile_found = False
                for tile_type in self.tiles_neat:
                    for tile in tile_type.sprites():
                        if tile.rect.x in range(row, row + 64) and tile.rect.y in range(column, column + 64):
                            if tile_type is self.terrain_tiles:
                                fov_array[j][i] = 1
                                tile_found = True
                            elif tile_type is self.tree_obs:
                                fov_array[j][i] = 2
                                tile_found = True
                            elif tile_type is self.enemy_tiles:
                                fov_array[j][i] = -1
                                tile_found = True
                            elif tile_type is self.objects_tiles:
                                fov_array[j][i] = 3
                                tile_found = True
                if not tile_found:
                    fov_array[j][i] = 0
                j += 1
            i += 1
        fov_array[pl_y][0] = 4
        return fov_array

    def move_right(self):
        self.keys['right'] = True

    def move_left(self):
        self.keys['left'] = True

    def move_up(self):
        self.keys['up'] = True

    def move_right_up(self):
        self.keys['right'] = True
        self.keys['up'] = True

    def move_left_up(self):
        self.keys['left'] = True
        self.keys['up'] = True

    def restore_keys(self):
        self.keys['right'] = False
        self.keys['left'] = False
        self.keys['up'] = False

    # def check_player_pos(self, player):
    #     if player.rect.x in range(self.player_prev_pos-4, self.player_prev_pos+4): # == self.player_prev_pos:
    #         stayed = True
    #     else:
    #         stayed = False
    #     self.player_prev_pos = player.rect.x
    #     return stayed

    def distance_traveled(self, player):
        self.shifted += -self.world_shift
        return player.rect.x + self.shifted

    def nparray_to_list(self):
        fv = self.fov(self.players.sprite)
        return fv.reshape(-1).tolist()

    def draw_level(self):
        """
        Running level following these consecutive steps:
        0. Draw background
        1. Processing external changes to player's state
        2. Update tiles and other non-player objects
        3. Process player's collisions
        4. Get player's new state according to new circumstances
        5. Draw everything
        """
        # 0.
        self.sky.draw(self.surface)
        self.clouds.draw(self.surface, self.world_shift)
        self.water.draw(self.surface, self.world_shift)

        # 1.
        self.start_music()
        self.restore_player_neat(self.players.sprite)
        self.apply_gravity(self.gravity)
        self.permit_jump(self.players.sprite)
        # self.return_to_menu(self.players.sprite)

        # 2.
        # self.keys['right'] = True
        self.players.sprite.get_keys(neat=True, keys=self.keys)
        # self.players.sprite.get_inputs()
        self.players.update()
        self.restore_keys()
        for tile in self.all_tiles:
            tile.update(self.world_shift)
        self.constrains.update(self.world_shift)
        self.tree_obs.update(self.world_shift)
        self.level_end.update(self.world_shift)

        # 3.
        self.collision_x_handler(self.players.sprite, self.terrain_tiles)
        self.collision_y_handler(self.players.sprite, self.terrain_tiles)
        self.tree_collision(self.players.sprite, self.tree_obs)
        self.objects_collision(self.players.sprite, self.objects_tiles)
        self.enemy_collision(self.players.sprite, self.enemy_tiles)
        self.level_finish(self.players.sprite, self.level_end)
        for enemy in self.enemy_tiles.sprites():
            self.enemy_constrains(enemy, self.constrains)
        self.scroll_x(self.players.sprite)

        # 4.
        # self.check_defeat(self.players.sprite)
        self.check_state(self.players.sprite)
        self.particle_create(self.players.sprite)
        log.info("-------------")

        # 5.
        for tile in self.all_tiles:
            tile.draw(self.surface)
        self.particle_draw(self.players.sprite, self.particles, self.run_particles)
        self.players.draw(self.surface)
        self.ui.draw()

        # fv = self.fov(self.players.sprite)
        # print(len(fv))
        # print(len(fv.reshape(-1).tolist())) # 50
        # print(fv.reshape(-1), type(fv.reshape(-1).tolist()))
        # print(fv)
        # print("-----------")

    def run(self):
        """
        Function for running level if player's hasn't been defeated
        """
        self.draw_level()
        # if self.check_defeat(self.players.sprite):
        #     self.goto_endscore()
        # else:
        #     self.draw_level()

