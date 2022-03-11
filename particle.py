import pygame
from settings import *
from utils import get_img, load_flipped


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
        # Images managing
        self.states = {"land": [], "jump": [], "run": [], "explosion": []}
        self.state = state
        self.prev_state = ""
        self.states = get_img(PARTICLE_IMAGES_DIR, self.states)
        self.flipped = load_flipped(self.states)
        self.flipped_flag = flipped

        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)

        # Animation parameters
        self.frame_index = 0
        self.animation_speed = ANIMATION_SPEED

    def animate(self):
        """
        Function for animation
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
        self.animate()

        if self.flipped_flag:
            self.image = self.flipped[self.state][int(self.frame_index)]
        self.prev_state = self.state

        if self.state != "run":
            self.rect.x += x_shift

