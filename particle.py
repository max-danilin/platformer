import pygame
import os
from settings import *


class Particle(pygame.sprite.Sprite):
    """
    Class for creating and drawing particles
    """
    def __init__(self, pos, state, flipped=False):
        """
        states - dict that contains images for different types of particles
        :param pos: position of sprite
        :param state: type of particle to create
        :param flipped: whether we should flip particle image
        """
        super().__init__()
        self.states = {"land": [], "jump": [], "run": [], "explosion": []}
        self.state = state
        self.prev_state = ""
        self.get_img(PARTICLE_IMAGES_DIR)

        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.flipped = flipped

        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED

    def get_img(self, img_dir):
        """
        Method for loading all images for all the states.
        :param img_dir: image directory
        :return:
        """
        for state in self.states:
            state_path = os.path.join(img_dir, state)
            for file in os.listdir(state_path):
                if file.lower().find(state) != -1:
                    path = os.path.join(state_path, file)
                    img_load = pygame.image.load(path).convert_alpha()
                    self.states[state].append(img_load)

    def update(self, x_shift):
        """
        Method for drawing particles sprites according to their state.
        We update particle positions separately because they depend on player's object.
        If we draw jumping or landing particles we need to kill them after animation is over.
        Also we flip particle sprites depending on player's facing direction and move jumping
        and landing particles if camera moves.
        :param x_shift: speed of camera movement
        :return:
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.states[self.state]):
            self.frame_index = 0
            if self.state != 'run':
                self.kill()
        if self.state != self.prev_state:
            self.frame_index = 0
        self.image = self.states[self.state][int(self.frame_index)]

        if self.flipped:
            self.image = pygame.transform.flip(self.image, True, False)
        self.prev_state = self.state

        if self.state != "run":
            self.rect.x += x_shift

