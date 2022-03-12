import pygame
from settings import *


class EndGame:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 60)

    def draw(self):
        self.surface.fill("black")
        surf_lost = self.font.render("YOU LOST!", True, "red")
        lost_rect = surf_lost.get_rect(midtop=(screen_width/2, screen_height/5))
        surf_coins = self.font.render(f"Coins: {self.player.coins}", True, "red")
        coins_rect = surf_coins.get_rect(midtop=(lost_rect.centerx, lost_rect.bottom+15))
        surf_levels = self.font.render(f"Levels completed: {self.player.levels_completed}", True, "red")
        levels_rect = surf_levels.get_rect(midtop=(coins_rect.centerx, coins_rect.bottom + 15))
        surf_enemies = self.font.render(f"Enemies destroyed: {self.player.enemies_killed}", True, "red")
        enemies_rect = surf_enemies.get_rect(midtop=(levels_rect.centerx, levels_rect.bottom + 15))
        self.surface.blit(surf_lost, lost_rect)
        self.surface.blit(surf_coins, coins_rect)
        self.surface.blit(surf_levels, levels_rect)
        self.surface.blit(surf_enemies, enemies_rect)
