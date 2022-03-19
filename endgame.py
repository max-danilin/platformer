import pygame
from settings import *


class EndGame:
    """
    Class for displaying endgame menu
    """
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.created = True

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 60)

        # Sound
        self.end_sound = pygame.mixer.Sound(GAMEOVER_SOUND_DIR)

    def play_sound(self):
        """
        Play sound when created
        :return:
        """
        if self.created:
            # channel = pygame.mixer.find_channel(force=True)
            # channel.play(self.end_sound)
            pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL+1).play(self.end_sound)

    def draw(self):
        """
        Displays end-game message with player's statistics
        :return:
        """
        self.play_sound()
        self.created = False

        self.surface.fill("black")
        # Message
        surf_lost = self.font.render("YOU LOST!", True, "red")
        lost_rect = surf_lost.get_rect(midtop=(screen_width/2, screen_height/5))
        # Coins gathered
        surf_coins = self.font.render(f"Coins: {self.player.coins}", True, "red")
        coins_rect = surf_coins.get_rect(midtop=(lost_rect.centerx, lost_rect.bottom+15))
        # Levels completed
        surf_levels = self.font.render(f"Levels completed: {self.player.levels_completed}", True, "red")
        levels_rect = surf_levels.get_rect(midtop=(coins_rect.centerx, coins_rect.bottom + 15))
        # Enemies destroyed
        surf_enemies = self.font.render(f"Enemies destroyed: {self.player.enemies_killed}", True, "red")
        enemies_rect = surf_enemies.get_rect(midtop=(levels_rect.centerx, levels_rect.bottom + 15))

        self.surface.blit(surf_lost, lost_rect)
        self.surface.blit(surf_coins, coins_rect)
        self.surface.blit(surf_levels, levels_rect)
        self.surface.blit(surf_enemies, enemies_rect)
