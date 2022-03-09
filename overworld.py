import pygame
from brick_level import LevelBrick
from player import Player
from settings import *
from collections import namedtuple


class Overworld:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.brick_levels = pygame.sprite.Group()
        self.players = pygame.sprite.GroupSingle()
        self.add_levels()
        self.points = [brick.rect.center for brick in self.brick_levels.sprites()]
        self.create_player()
        self.proceed_to_level = None

    def add_levels(self):
        level_bricks_list = []
        for level in level_bricks:
            level_bricks_list.append(LevelBrick(**level_bricks[level]))
        for level in level_bricks_list:
            self.brick_levels.add(level)

    def create_player(self):
        self.player.rect.center = self.points[0]
        self.players.add(self.player)

    @staticmethod
    def line_equation(x, p0, p1):
        y = (x - p0.x) / (p1.x - p0.x) * (p1.y - p0.y) + p0.y
        return int(y)

    def player_constraints(self):
        sprite = self.players.sprite
        if sprite.rect.x <= level_bricks['level_0']['pos'][0]:
            sprite.direction.x, sprite.direction.y = 0, 0
            sprite.rect.x = level_bricks['level_0']['pos'][0]
        elif sprite.rect.x >= level_bricks['level_3']['pos'][0]:
            sprite.direction.x, sprite.direction.y = 0, 0
            sprite.rect.x = level_bricks['level_3']['pos'][0]

    def player_movement(self):
        sprite = self.players.sprite
        point = namedtuple("Point", "x, y")
        if sprite.rect.centerx in range(self.points[0][0], self.points[1][0]):
            sprite.rect.centery = self.line_equation(sprite.rect.centerx, point(*self.points[0]), point(*self.points[1]))
        elif sprite.rect.centerx in range(self.points[1][0], self.points[2][0]):
            sprite.rect.centery = self.line_equation(sprite.rect.centerx, point(*self.points[1]), point(*self.points[2]))
        elif sprite.rect.centerx in range(self.points[2][0], self.points[3][0]):
            sprite.rect.centery = self.line_equation(sprite.rect.centerx, point(*self.points[2]), point(*self.points[3]))

    def player_set_animation(self):
        sprite = self.players.sprite
        if sprite.direction.x != 0:
            sprite.state = "run"
        else:
            sprite.state = "idle"

    def check_position(self):
        sprite = self.players.sprite
        for brick in self.brick_levels.sprites():
            if sprite.rect.centerx in range(brick.rect.x, brick.rect.right) \
                    and sprite.rect.centery in range(brick.rect.top, brick.rect.bottom):
                return brick

    def go_to_level(self):
        keys = pygame.key.get_pressed()
        brick = self.check_position()
        if brick and keys[pygame.K_RETURN] and brick.activate:
            self.proceed_to_level = True
            return brick
        else:
            return None

    def get_brick_by_level(self, level):
        for brick in self.brick_levels.sprites():
            if level == brick.name:
                return brick

    def check_level_activation(self):
        for brick in self.brick_levels.sprites():
            required_level = []
            if not brick.activate:
                for level in brick.for_activation:
                    lb = self.get_brick_by_level(level)
                    required_level.append(lb.completed)
                if all(required_level):
                    brick.activate = True

    def draw_lines(self):
        pygame.draw.lines(self.surface, 'red', False, self.points, 10)

    def run(self):
        self.brick_levels.update()
        self.player_constraints()
        self.players.update()
        self.player_movement()
        self.player_set_animation()
        self.go_to_level()
        self.draw_lines()
        self.brick_levels.draw(self.surface)
        self.players.draw(self.surface)