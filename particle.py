import pygame
import os


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.states = {"land": [], "jump": [], "run": []}
        self.state = "land"
        self.prev_state = ""
        self.get_img("dust_particles")
        self.frame_index = 0
        self.animation_speed = 0.15
        self.pos = pos
        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)

    def get_img(self, img_dir):
        for state in self.states:
            state_path = os.path.join(img_dir, state)
            for file in os.listdir(state_path):
                if file.lower().find(state) != -1:
                    path = os.path.join(state_path, file)
                    img_load = pygame.image.load(path).convert_alpha()
                    self.states[state].append(img_load)

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.states[self.state]):
            if self.state == 'run':
                self.frame_index = 0
            else:
                self.kill()
        if self.state != self.prev_state:
            self.frame_index = 0
        print(self.frame_index, self.states[self.state][int(self.frame_index)])
        self.image = self.states[self.state][int(self.frame_index)]
        self.prev_state = self.state
        #self.rect = self.image.get_rect(topleft=self.pos)

