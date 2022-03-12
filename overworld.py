import pygame
from brick_level import LevelBrick
from settings import *
from collections import namedtuple
from decoration import Sky


class Overworld:
    """
    Class for processing overworld level
    """
    def __init__(self, surface, player):
        """
        points - central points of level bricks to draw routes
        ava_points - central points of available brick levels
        compl_brick - level that player tries to access while it was completed
        :param surface:
        :param player:
        """
        self.surface = surface
        self.player = player

        # Create overworld
        self.brick_levels = pygame.sprite.Group()
        self.players = pygame.sprite.GroupSingle()
        self.add_levels()

        self.points = [brick.rect.center for brick in self.brick_levels.sprites()]

        # Flags and parameters
        self.ava_points = None
        self.ava_bricks = None
        self.compl_brick = None
        self.proceed_to_level = None
        self.running = False
        self.victory = False
        self.player_pos = self.points[0]

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
        level_bricks_list = []
        for level in level_bricks:
            level_brick = LevelBrick(**level_bricks[level])
            level_bricks_list.append(level_brick)
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

    def check_bricks(self):
        """
        Function to get brick levels, available at the moment. Sorted by X coordinate
        :return: last available brick
        """
        avail_bricks = [brick for brick in self.brick_levels.sprites() if brick.activate]
        self.ava_bricks = sorted(avail_bricks, key=lambda item: item.rect.x)

    def check_points(self):
        self.ava_points = [brick.rect.center for brick in self.brick_levels.sprites() if brick.activate]

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
        if x in range(self.points[0][0], self.points[1][0]):
            player.rect.centery = self.line_equation(x, point(*self.points[0]), point(*self.points[1]))
        elif x in range(self.points[1][0], self.points[2][0]):
            player.rect.centery = self.line_equation(x, point(*self.points[1]), point(*self.points[2]))
        elif x in range(self.points[2][0], self.points[3][0]):
            player.rect.centery = self.line_equation(x, point(*self.points[2]), point(*self.points[3]))

    def set_player(self, player):
        """
        Setting player in the overworld
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
        Function to go to given level
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

    def check_victory(self):
        self.victory = all([level.completed for level in self.brick_levels.sprites()])

    def check_state(self):
        """
        Prepare overworld and player when overworld is started
        :return:
        """
        if not self.running:
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).play(self.overworld_music, loops=-1)
            self.check_level_activation()
            self.check_bricks()
            self.check_points()
            self.set_player(self.players.sprite)
            self.running = True
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
        Check if requirements for level activation are fulfilled
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
        pygame.draw.lines(self.surface, 'red', False, self.ava_points, 10)

    def run(self):
        # Creating level
        self.check_state()
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