import pygame
import os
from maker import refactor_image
from math import ceil
from settings import *

# Create images if they haven't been created before
img_dir = PLAYER_IMAGES_DIR
if not os.path.exists(img_dir):
    refactor_image(54, 60)


class Player(pygame.sprite.Sprite):
    """
    Class for player object
    """
    def __init__(self, pos):
        """
        states - dict that contains images for different states of the player
        exact x and y - rounded up coordinates for collision detection
        shift_speed - variable to preserve speed value for level's world shifting
        :param pos: position of player's sprite
        """
        super().__init__()
        self.states = {"idle": [], "jump": [], "run": []}
        self.state = "idle"
        self.prev_state = ""
        self.get_img(img_dir)

        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)

        self.exact_x, self.exact_y = float(self.rect.x), float(self.rect.y)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = pygame.math.Vector2(PLAYER_SPEED, 1)
        # We don't actually use speed.y, but its more convenient to keep it this way
        self.shift_speed = self.speed.x
        self.jump_speed = JUMP_SPEED

        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED
        self.moving_right = True

    def get_img(self, dir):  # TODO maybe place this and particle's method in utils
        """
        Method for loading all images for all the states.
        :param dir: image directory
        :return:
        """
        for file in os.listdir(dir):
            for state in self.states:
                if file.lower().find(state) != -1:
                    path = os.path.join(dir, file)
                    img_load = pygame.image.load(path).convert_alpha()
                    self.states[state].append(img_load)

    def get_inputs(self):
        """
        Method for getting inputs for moving right or left.
        :return:
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.moving_right = False
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.moving_right = True
        else:
            self.direction.x = 0

    def update(self):
        """
        Method for updating player's position and animation.
        First, we check inputs, then update positions and rounded up positions (we need them for
        collision detection) and afterwards deal with animations. We cycle animations and restart them if player's
        state has changed from previous frame. Also flip the image if player pressed movement button.
        We save speed in order to implement camera movement aka level's world shift.
        :return:
        """
        self.get_inputs()

        self.exact_x = ceil(self.rect.x + self.direction.x * self.speed.x)
        self.exact_y = ceil(self.rect.y + self.direction.y)
        self.rect.x += self.direction.x * self.speed.x
        self.rect.y += self.direction.y

        self.frame_index += self.animation_speed
        if self.state != self.prev_state:
            self.frame_index = 0
        if self.frame_index >= len(self.states[self.state]):
            self.frame_index = 0
        self.image = self.states[self.state][int(self.frame_index)]

        if not self.moving_right:
            self.image = pygame.transform.flip(self.image, True, False)

        self.prev_state = self.state
        self.speed.x = self.shift_speed

    def jump(self):
        """
        This method needs to be implemented separately because jumping can occur only while on ground.
        :return:
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = self.jump_speed



