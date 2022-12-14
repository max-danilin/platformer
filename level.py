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

    def __init__(self, level_data, surface, player, ui, neat=False, multiple_players=False, draw=True):
        """
        world_shift - allows us to move camera when player reaches certain lines on the screen
        back_to_menu - flag to check if game should get back to overworld
        postponed - flag to pause level if backspace was hit
        endgame - class for endgame screen
        neat_tiles - tiles level should treat as objects affected by world shift for NEAT to work properly
        furthest_saved - saves furthest player from previous run
        furthest_changed - whether furthest player has changed since last run
        furthest - player with most X position of all
        :param player - player's object
        :param ui - player's UI
        :param level_data: level map in txt format
        :param surface: surface to draw on
        :param neat - whether a player will be managed by NEAT
        :param multiple_players - whether level will be handling multiple AI players
        """
        if not isinstance(level_data, dict):
            raise LevelError(f'Level data should be dict, not {type(level_data)}')
        self.level_data = level_data
        self.surface = surface
        self.player = player
        self.ui = ui
        self.endgame = EndGame(self.surface, self.player)
        self.neat = neat
        self.multiple_players = multiple_players
        self.draw = draw

        # Local level variables
        self.world_shift = 0
        self.gravity = GRAVITY
        self.level_width = 0

        # Flags
        self.completed = False
        self.back_to_menu = False
        self.postponed = True
        self.started = True

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
        if not self.multiple_players:
            self.players = pygame.sprite.GroupSingle()
        else:
            self.players = pygame.sprite.Group()

        self.preloaded = Level.preload_images()
        [self.create_tile_group(key) for key in self.level_data]

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

        # Neat
        self.tiles_neat = [self.terrain_tiles, self.enemy_tiles, self.objects_tiles, self.tree_obs]
        # Neat multiple players
        self.furthest_saved = None
        self.furthest_changed = False
        self.furthest = None
        self.max_x = 0
        self.prev_shift = 0

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
                            if self.multiple_players:
                                for player in self.player:
                                    player.rect.topleft = (x, y)
                                    self.players.add(player)
                            else:
                                self.player.rect.topleft = (x, y)
                                self.players.add(self.player)
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

    @staticmethod
    def apply_gravity(gravity, player):
        """
        Applying gravity onto player object
        :return: None
        """
        if not isinstance(gravity, int) and not isinstance(gravity, float):
            raise LevelError(f"Gravity should be number, not {type(gravity)}")
        player.direction.y += gravity

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
        if player.on_ground:
            player.get_keys(neat=self.neat)
            player.jump(self.draw)

    def goto_endscore(self):
        """
        Draws end scene. Unused if NEAT is running.
        :return:
        """
        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL + 2).stop()
        self.endgame.draw()

    def check_defeat(self, player):
        """
        Checks if player has fallen or has no lives left. Removes player from group in case of multiple players
        :param player: player object
        :return: True if the player was defeated
        """
        if player.rect.y >= screen_height or player.lives <= 0:
            if self.multiple_players:
                self.players.remove(player)
            return True
        else:
            return False

    @staticmethod
    def tree_collision(player, trees):
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
                player.on_ground = True
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
                if self.draw:
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
                    if self.draw:
                        self.stomp_sound.play()
                    enemies.remove(enemy)
                    player.enemies_killed += 1
                    killed = True
                else:
                    now = pygame.time.get_ticks()
                    if now - player.last_hit >= AFTER_DAMAGE_INVUL:
                        player.last_hit = now
                        if self.draw:
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
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL + 2).stop()
            player.levels_completed += 1
            self.completed = True

    @staticmethod
    def save_player(player):
        """
        Method for saving player's parameters when the level is created and if it is paused. Unused if NEAT is running.
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
        if not self.neat:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_BACKSPACE]:
                pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL + 2).stop()
                self.back_to_menu = True
                self.postponed = True
                player.pps = self.save_player(player)

    def restore_player(self, player):
        """
        Restores player parameters if level is resumed. Unused if NEAT is running.
        :param player:
        :return:
        """
        if self.postponed:
            if not self.neat:
                (player.rect.x, player.rect.y), (player.direction.x, player.direction.y), (
                    player.speed.x, player.speed.y) = player.pps
            self.postponed = False

    @staticmethod
    def collision_x_handler(player, tiles):
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

    @staticmethod
    def collision_y_handler(player, tiles):
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
        player.on_ground = False

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
                player.on_ground = True
                log.debug(f"COLLIDE Y: player x={player.rect.x}, player bottom={player.rect.bottom};"
                          f" tile x={tile.rect.x}, tile top={tile.rect.top}")
        player.rect.y = saving_position if not collided_y else player.rect.y

    @staticmethod
    def check_state(player):
        """
        Method for determining player's state for correct animations.
        :param player: player's sprite
        :return:
        """
        if player.direction.x == 0 and player.on_ground:
            player.state = "idle"
        elif player.direction.x != 0 and player.on_ground:
            player.state = "run"
        else:
            player.state = "jump"
        log.info(f"State = {player.state}, direction x = {player.direction.x}, direction y = {player.direction.y},"
                 f" rect y = {player.rect.y}, rect x = {player.rect.x}, on ground = {player.on_ground}")

    def particle_create(self, player):
        """
        Method for creating jump, landing and running particles based on
        player's state and position.
        :param player: player's sprite
        """
        if player.prev_state != "jump" and player.direction.y < 0:
            particle_offset = pygame.math.Vector2(-10, 30)
            jump_particle = Particle(player.rect.bottomleft - particle_offset, 'jump')
            self.particles.add(jump_particle)
            log.debug(f"Jump particle created {jump_particle.rect.x}, {jump_particle.rect.y}")
        elif player.prev_state == "jump" and player.on_ground:
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
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL + 2).set_volume(0.03)
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL+2).play(self.level_music, loops=-1)

    # Neat functions
    ############################

    def fov(self, player):
        """
        Determines field of view for ai of a player. We set up a 2 dimensional array for FOV_DISTANCE *
        (screen_height - 1) squares and fill it with values based on what type of tile is located inside this square.
        We start filling based on player's x position ang go on for FOV_DISTANCE squares (square consists of
        tile size * tile size pixels).
        We make distinctions between these objects:
        0 - no tile
        1 - terrain tile
        2 - tree obstacles (have to distinct them from terrain, because their collision works different)
        3 - objects like coins
        4 - player itself (might try not inserting it into array)
        -1 - enemy tiles
        It might be useful to try different ways of detecting enemies and player inside the square, like based on
        X position or central position or even trying to let enemy fill all the squares where it was detected.
        we also might try to spread FOV to the left of the player since it can move towards that direction by
        changing LEFT_FOV_ADJUSTMENT value. REMINDER: in doing you you should also change input value in
        config.txt to 10 * LEFT_FOV_ADJUSTMENT.
        :param player:
        :return: fov 2d array
        """
        pl_x = int((player.rect.x + player.speed.x + 1) // tile_size)
        pl_y = int(player.rect.y // tile_size) - 1
        fov_array = numpy.empty(((screen_height // tile_size) - 1, FOV_DISTANCE + LEFT_FOV_ADJUSTMENT))
        column = 0
        for x in range((pl_x - LEFT_FOV_ADJUSTMENT) * tile_size, (pl_x + FOV_DISTANCE) * tile_size, tile_size):
            row = 0
            for y in range(tile_size, screen_height, tile_size):
                tile_found = False
                for tile_type in self.tiles_neat:
                    for tile in tile_type.sprites():
                        if tile.rect.x in range(x, x + tile_size) and tile.rect.y in range(y, y + tile_size):
                            if tile_type is self.terrain_tiles:
                                fov_array[row][column] = 1
                                tile_found = True
                            elif tile_type is self.tree_obs:
                                fov_array[row][column] = 2
                                tile_found = True
                            elif tile_type is self.enemy_tiles:
                                fov_array[row][column] = -1
                                tile_found = True
                            elif tile_type is self.objects_tiles:
                                fov_array[row][column] = 3
                                tile_found = True
                if not tile_found:
                    fov_array[row][column] = 0
                row += 1
            column += 1
        fov_array[pl_y][LEFT_FOV_ADJUSTMENT] = 4
        # print(fov_array)
        # print("----------------------")
        return fov_array

    def distance_traveled(self, player):
        """
        Detects how much distance in the level player has moved
        shifted - increases as player reaches edge of the screen
        Also distance shouldnt be affected when screen is moved for the firsth time, cause
        we change only player's speed, not his position when shifting
        :param player:
        :return: distance
        """
        if self.prev_shift == 0 and self.world_shift != 0:
            pass
        else:
            player.shifted += -self.world_shift
        self.prev_shift = self.world_shift
        return player.rect.x + player.shifted

    def nparray_to_list(self, player):
        """
        Convert 2d array into list with multiple values for feeding to neural network as input
        :return: list
        """
        fv = self.fov(player)
        return fv.reshape(-1).tolist()

    ############################

    def remove_player(self, player):
        self.players.remove(player)

    def get_futher(self, players):
        """
        Get player, covered most distance among all players. Camera will be focused on this player while it remains
        furthest and alive. If that player is changed, revert camera to the next such player.
        max_x - get X position of saved furthest player
        """
        self.furthest = sorted(players, key=lambda player: player.rect.x, reverse=True)[0]
        if self.furthest is self.furthest_saved:
            self.furthest_changed = False
            self.max_x = self.furthest_saved.rect.x
        else:
            self.furthest_changed = True
            self.revert_camera()
        self.furthest_saved = self.furthest

    def revert_camera(self):
        """
        Revert camera to the position of the next furthest player based on the difference between it's X position
        and X position of previous furthest player
        """
        dist = self.furthest.rect.x
        self.world_shift = self.max_x - dist

    def move_other(self, players):
        """
        Affect other players with world's shift based on furthest player movement
        """
        for player in players:
            if player is self.furthest:
                pass
            else:
                player.rect.x += self.world_shift

    def draw_multiple(self):
        """
        :param draw: whether to draw Level(useful for NEAT implementation)
        Running level with NEAT multiple players:
        0. Draw background
        1. Processing external changes to players states
        2. Update tiles and other non-player objects
        3. Process players collisions with other objects
        4. Get players new states according to new circumstances
        5. Draw everything if draw is True
        We don't process particles when dealing with multiple players to make calculations easier.
        """
        # 0.
        if self.draw:
            self.sky.draw(self.surface)
            self.clouds.draw(self.surface, self.world_shift)
            self.water.draw(self.surface, self.world_shift)
            self.start_music()

        # 1.
        for player in self.players.sprites():
            self.restore_player(player)
            self.apply_gravity(self.gravity, player)
            self.permit_jump(player)
            player.get_keys(neat=self.neat)

        # 2.
        self.players.update()
        for tile in self.all_tiles:
            tile.update(self.world_shift)
        self.constrains.update(self.world_shift)
        self.tree_obs.update(self.world_shift)
        self.level_end.update(self.world_shift)

        # 3.
        for player in self.players.sprites():
            self.collision_x_handler(player, self.terrain_tiles)
            self.collision_y_handler(player, self.terrain_tiles)
            self.tree_collision(player, self.tree_obs)
            self.objects_collision(player, self.objects_tiles)
            self.enemy_collision(player, self.enemy_tiles)
            self.level_finish(player, self.level_end)
        for enemy in self.enemy_tiles.sprites():
            self.enemy_constrains(enemy, self.constrains)
        if self.multiple_players:
            self.get_futher(self.players.sprites())
            if not self.furthest_changed:
                self.scroll_x(self.furthest)
            self.move_other(self.players.sprites())
        else:
            self.scroll_x(self.players.sprite)

        # 4.
        for player in self.players.sprites():
            self.check_state(player)
        log.info("-------------")

        # 5.
        if self.draw:
            for tile in self.all_tiles:
                tile.draw(self.surface)
            self.players.draw(self.surface)

    def draw_level(self):
        """
        :param draw: whether to draw Level(useful for NEAT implementation)
        Running level following these consecutive steps:
        0. Draw background
        1. Processing external changes to player's state
        2. Update tiles and other non-player objects
        3. Process player's collisions
        4. Get player's new state according to new circumstances
        5. Draw everything
        """
        # 0.
        if self.draw:
            self.sky.draw(self.surface)
            self.clouds.draw(self.surface, self.world_shift)
            self.water.draw(self.surface, self.world_shift)
            self.start_music()

        # 1.
        self.restore_player(self.players.sprite)
        self.apply_gravity(self.gravity, self.players.sprite)
        self.permit_jump(self.players.sprite)
        self.return_to_menu(self.players.sprite)

        # 2.
        self.players.sprite.get_keys(neat=self.neat)
        self.players.update()
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
        self.check_state(self.players.sprite)
        self.particle_create(self.players.sprite)
        log.info("-------------")

        # 5.
        if self.draw:
            for tile in self.all_tiles:
                tile.draw(self.surface)
            self.particle_draw(self.players.sprite, self.particles, self.run_particles)
            self.players.draw(self.surface)
            self.ui.draw()

    def run(self):
        """
        Function for running level depending on NEAT mode and whether player has been defeated
        """
        if self.neat:
            if self.multiple_players:
                self.draw_multiple()
            else:
                self.draw_level()
        else:
            if self.check_defeat(self.players.sprite):
                self.goto_endscore()
            else:
                self.draw_level()

