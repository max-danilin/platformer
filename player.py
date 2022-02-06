import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        #self.image = pygame.Surface((32, 64))
        self.image = pygame.image.load('img/1.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = pygame.math.Vector2(5, 1)
        self.jump_speed = -13

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
        self.rect.x += self.direction.x * self.speed.x
        self.rect.y += self.direction.y

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = self.jump_speed



