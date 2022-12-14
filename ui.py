import pygame
from settings import *


class UI:
    """
    Class for displaying player's UI
    """
    def __init__(self, surface, player):
        """
        Initialize displaying coins and health bar. Create additional rect for coins to align both image and text.
        :param surface:
        :param player:
        """
        self.player = player
        self.surface = surface

        # Coin
        self.coin_img = pygame.image.load(UI_COIN_DIR).convert_alpha()
        self.coin_rect = self.coin_img.get_rect(topleft=(40, 80))

        # Health bar
        self.health_img = pygame.image.load(UI_HB_DIR).convert_alpha()
        self.hb_start = HELTH_BAR_POS
        self.hb_width = 152
        self.hb_height = 4
        self.hp_color = HEALTH_BAR_COLOR

        # Font
        pygame.font.init()
        self.font = pygame.font.Font(UI_FONT_DIR, 30)
        self.check_parameters()

    def check_parameters(self):
        if not isinstance(self.hb_start, tuple) and not isinstance(self.hb_start, list):
            raise TypeError(f'Health bar positions should be tuple or list, not {type(self.hb_start)}')

    def get_current_hp(self):
        """
        Determine ration for remaining health of the player and drawing corresponding rect.
        :return:
        """
        if self.player.lives > self.player.max_lives:
            ratio = 1
        else:
            ratio = self.player.lives / self.player.max_lives
        width = ratio * self.hb_width
        hb_rect = pygame.Rect(self.hb_start, (width, self.hb_height))
        return hb_rect

    def draw(self):
        """
        Method for drawing
        :return:
        """
        # Display number of coins
        surf_coins = self.font.render(str(self.player.coins), True, 'black')
        coin_rect = surf_coins.get_rect(midleft=(self.coin_rect.right+5, self.coin_rect.centery))
        self.surface.blit(surf_coins, coin_rect)

        # Display images
        self.surface.blit(self.coin_img, self.coin_rect)
        self.surface.blit(self.health_img, (40, 20))

        pygame.draw.rect(self.surface, self.hp_color, self.get_current_hp())
