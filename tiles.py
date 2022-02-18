import pygame


class Tile(pygame.sprite.Sprite):
    """
    Class for creating sprites of tiles
    """
    def __init__(self, size, pos, img):
        """
        :param size: size of a tile
        :param pos: position of a tile
        """
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        """
        Method for updating tiles position if camera moves.
        :param x_shift: speed of camera movement
        :return:
        """
        self.rect.x += x_shift


class StaticTile(Tile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y+size))


class CollisionTreeTile(StaticTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)


class AnimatedTile(Tile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)

    def animate(self):
        pass


class ObjectTile(AnimatedTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x+15, y+size))


class EnemyTile(AnimatedTile):
    def __init__(self, size, pos, img):
        super().__init__(size, pos, img)

