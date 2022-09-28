import pygame
from brick_level import LevelBrick
from settings import *
from collections import namedtuple
from decoration import Sky
from victory import Victory
from ui import UI
from time import time


class Overworld:
    """
    Class for processing overworld level
    """
    def __init__(self, surface, player):
        """
        points - central points of level bricks to draw routes
        ava_bricks - list of bricks that represent available levels at the moment, needed mostly for constraints
        ava_points - central points of available brick levels to draw paths
        compl_brick - level that player tries to access while it was completed
        ui - create player's UI
        victory - create Victory class for victory screen
        proceed_to_level - brick level that was chosen
        started - whether overworld was launched at this frame
        player_pos - saving position of player in the overworld to restore it when game returns to overworld
        :param surface:
        :param player:
        """
        self.surface = surface
        self.player = player
        self.victory = Victory(self.surface, self.player)
        self.ui = UI(self.surface, self.player)

        # Create overworld
        self.brick_levels = pygame.sprite.Group()
        self.players = pygame.sprite.GroupSingle()
        self.add_levels()

        self.points = [brick.rect.center for brick in self.brick_levels.sprites()]

        # Flags and parameters
            # Bricks
        self.ava_points = list()
        self.ava_bricks = list()
        self.compl_brick = None
            # Flags
        self.proceed_to_level = None
        self.started = False
        self.player_pos = self.points[0]
        self.escape_timeout = time()

        self.create_player()

        self.sky = Sky(8)

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 30)

        # Music
        self.overworld_music = pygame.mixer.Sound(OVERWORLD_MUSIC_DIR)

    def add_levels(self):
        """
        Function for creating brick levels from dictionary level_bricks and adding them to sprite group.
        :return:
        """
        for level in level_bricks:
            level_brick = LevelBrick(**level_bricks[level])
            self.brick_levels.add(level_brick)

    def create_player(self):
        """
        Function for placing player in the middle of the first brick level
        :return:
        """
        self.player.rect.center = self.points[0]
        self.players.add(self.player)

    @staticmethod
    def line_equation(x, p0, p1):
        """
        Line equation from two points
        """
        y = (x - p0.x) / (p1.x - p0.x) * (p1.y - p0.y) + p0.y
        return int(y)

    def check_available(self):
        """
        Function to get brick levels and their central points, available at the moment. Sorted by X coordinate
        """
        ava_points = []
        ava_bricks = []
        for brick in self.brick_levels.sprites():
            if brick.activate:
                ava_bricks.append(brick)
                ava_points.append(brick.rect.center)
        self.ava_points = ava_points
        self.ava_bricks = ava_bricks
        self.ava_bricks = sorted(self.ava_bricks, key=lambda item: item.rect.x)

    @staticmethod
    def player_constraints(player, avail):
        """
        Function to determine where player can move inside overworld.
        We put boundaries within available blocks
        :return:
        """
        if player.rect.x <= avail[0].rect.x:
            player.direction.x, player.direction.y = 0, 0
            player.rect.x = avail[0].rect.x
        elif player.rect.right >= avail[-1].rect.right:
            player.direction.x, player.direction.y = 0, 0
            player.rect.right = avail[-1].rect.right

    def player_movement(self, player):
        """
        Function to determine player's movement along Y axis, based on line equation
        :return:
        """
        x = player.rect.centerx
        point = namedtuple("Point", "x, y")
        for i in range(len(self.points)-1):
            if x in range(self.points[i][0], self.points[i+1][0]):
                player.rect.centery = self.line_equation(x, point(*self.points[i]), point(*self.points[i+1]))

    def return_timeout(self):
        """
        Allows returning from overworld to initial screen only after some timeout after returning to overworld from game
        :return:
        """
        if time() - self.escape_timeout < OVERWORLD_ESCAPE_TIMEOUT:
            return False
        else:
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).stop()
            return True

    def set_player(self, player):
        """
        Setting player in the overworld after each level completion
        :param player:
        :return:
        """
        player.direction.x = 0
        player.direction.y = 0
        player.rect.center = self.player_pos

    @staticmethod
    def player_set_animation(player):
        """
        Set state of player's animation
        :return:
        """
        if player.direction.x != 0:
            player.state = "run"
        else:
            player.state = "idle"

    def check_position(self, player):
        """
        Checks player position relatively to activated brick levels
        :return: brick level if player in its borders
        """
        for brick in self.ava_bricks:
            if player.rect.centerx in range(brick.rect.x, brick.rect.right) \
                    and player.rect.centery in range(brick.rect.top, brick.rect.bottom):
                return brick

    def go_to_level(self):
        """
        Function to go to given level if ENTER key is hit. If brick is already completed, set flag to True
        Otherwise save chosen level and player's position in overworld
        :return:
        """
        keys = pygame.key.get_pressed()
        brick = self.check_position(self.players.sprite)
        if brick and keys[pygame.K_RETURN]:
            if brick.completed:
                self.compl_brick = brick
            else:
                self.proceed_to_level = brick
                self.player_pos = brick.rect.center

    def run_brick(self, brick):
        """
        Function for running level, associated with given brick level. Check if brick returns any of the stopping flags
        :param brick:
        :return:
        """
        if not brick.stop_level:
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).stop()
            brick.run_level(self.surface, self.player, self.ui)
        else:
            self.proceed_to_level = None
            self.started = False
            self.escape_timeout = time()
            brick.stop_level = False

    def check_victory(self):
        """
        Checks if all levels were completed
        :return:
        """
        return all([level.completed for level in self.brick_levels.sprites()])

    def set_state(self):
        """
        Prepare overworld and player when overworld is started
        :return:
        """
        if not self.started:
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).set_volume(0.03)
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).play(self.overworld_music, loops=-1)
            self.check_level_activation()
            self.check_available()
            self.set_player(self.players.sprite)
            self.started = True
            self.compl_brick = None

    def completed_level(self, level):
        """
        Function for displaying message for completed level
        :param level: level to mention in message
        :return:
        """
        if level:
            surf_completed = self.font.render(f"LeveL {level.name} was completed!", True, 'red')
            self.surface.blit(surf_completed, (screen_width/2-40, screen_width/2-20))

    def check_level_activation(self):
        """
        Check if requirements for level activation are fulfilled for each brick and if so, activate it
        :return:
        """
        for brick in self.brick_levels.sprites():
            if not brick.activate:
                if {level for level in brick.for_activation if brick.for_activation}.issubset(
                        {brick.name for brick in self.brick_levels.sprites() if brick.completed}):
                    brick.activate = True
                    brick.is_activated()

    def draw_lines(self):
        """
        Draw lines between center points of brick levels
        :return:
        """
        pygame.draw.lines(self.surface, 'black', False, self.points, 10)
        if len(self.ava_points) > 1:
            pygame.draw.lines(self.surface, 'red', False, self.ava_points, 10)

    def draw_overworld(self):
        """
        Function for drawing overworld
        :return:
        """
        # Creating level
        self.set_state()
        self.sky.draw(self.surface)
        self.brick_levels.update()

        # Player interactions
        self.players.update()
        self.player_movement(self.players.sprite)
        self.player_constraints(self.players.sprite, self.ava_bricks)
        self.player_set_animation(self.players.sprite)
        self.go_to_level()

        # Drawing objects
        self.draw_lines()
        self.brick_levels.draw(self.surface)
        self.players.draw(self.surface)
        self.completed_level(self.compl_brick)

    def run(self, events):
        """
        Function for running overworld. Draws overworld except for few scenarios:
        - player has won, then proceed to victory
        - player has selected level, then proceed to level
        :param events:
        :return:
        """
        if self.check_victory():
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).stop()
            self.victory.draw(events)
        elif self.proceed_to_level and not self.check_victory():
            self.run_brick(self.proceed_to_level)
        else:
            self.draw_overworld()
