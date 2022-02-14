import pygame


class Tile(pygame.sprite.Sprite):
    """
    Class for creating sprites of tiles
    """
    def __init__(self, size, pos):
        """
        :param size: size of a tile
        :param pos: position of a tile
        """
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('white')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        """
        Method for updating tiles position if camera moves.
        :param x_shift: speed of camera movement
        :return:
        """
        self.rect.x += x_shift
