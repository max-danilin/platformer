import pygame
import os
from maker import refactor_image
from math import ceil
from settings import *
from utils import get_img, load_flipped

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

        # Processing images
        self.all_states = ('idle', "jump", "run")
        self.state = "idle"
        self.prev_state = ""
        self.states = get_img(img_dir, self.all_states)
        self.flipped = load_flipped(self.states)
        self.changed = False

        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)

        # Player's state in space
        self.exact_x, self.exact_y = float(self.rect.x), float(self.rect.y)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = pygame.math.Vector2(PLAYER_SPEED, 1)
        # We don't actually use speed.y, but its more convenient to keep it this way
        self.shift_speed = self.speed.x
        self.jump_speed = JUMP_SPEED

        # Player internal parameters
        self.last_hit = pygame.time.get_ticks()
        self.max_lives = 5
        self.lives = 5
        self.coins = 0
        self.levels_completed = 0
        self.enemies_killed = 0
        self.blinks = BLINKING_DURATION

        # Sound
        self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_DIR)
        self.jump_sound.set_volume(0.1)

        # Animation parameters
        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED
        self.moving_right = True

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

    def if_blinked(self):
        """
        Revert image transparency back
        :return:
        """
        if self.changed:
            self.image.set_alpha(255)
            self.changed = False

    def animate(self):
        """
        Function for animation
        :return:
        """
        self.frame_index += self.animation_speed
        if self.state != self.prev_state:
            self.frame_index = 0
        if self.frame_index >= len(self.states[self.state]):
            self.frame_index = 0
        self.image = self.states[self.state][int(self.frame_index)]
        if not self.moving_right:
            self.image = self.flipped[self.state][int(self.frame_index)]

    def update(self):
        """
        Method for updating player's position and animation.
        First, we check inputs, then process blinked images, then update positions and rounded up positions
        (we need them for collision detection) and afterwards deal with animations. We cycle animations and
        restart them if player's state has changed from previous frame. Also flip the image if player pressed
        movement button.
        We save speed in order to implement camera movement aka level's world shift.
        :return:
        """

        self.get_inputs()
        self.if_blinked()

        self.exact_x = ceil(self.rect.x + self.direction.x * self.speed.x)
        self.exact_y = ceil(self.rect.y + self.direction.y)
        self.rect.x += self.direction.x * self.speed.x
        self.rect.y += self.direction.y

        self.animate()
        self.prev_state = self.state
        self.speed.x = self.shift_speed
        self.blinking()

    def blinking(self):
        """
        Function for blinking
        :return:
        """
        if self.blinks < BLINKING_DURATION:
            if not self.blinks % 2:
                self.image.set_alpha(0)
                self.changed = True
            self.blinks += 1

    def jump(self):
        """
        This method needs to be implemented separately because jumping can occur only while on ground.
        :return:
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = self.jump_speed
            self.jump_sound.play()
