import pygame
import os
from maker import refactor_image, new_dir

img_dir = new_dir
if not os.path.exists(img_dir):
    refactor_image(54, 60)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        #self.image = pygame.Surface((32, 64))
        self.states = {"idle": [], "jump": [], "run": []}
        self.state = "idle"
        self.prev_state = ""
        self.get_img()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.moving_right = True
        self.image = self.states[self.state][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = pygame.math.Vector2(5, 1)
        self.jump_speed = -13

    def get_img(self):
        for file in os.listdir(img_dir):
            for state in self.states:
                if file.lower().find(state) != -1:
                    path = os.path.join(img_dir, file)
                    img_load = pygame.image.load(path).convert_alpha()
                    self.states[state].append(img_load)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.moving_right = False
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.moving_right = True
        else:
            self.direction.x = 0
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

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = self.jump_speed



