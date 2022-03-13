import pygame
from settings import *
from highscore import HighScore


class Victory:
    """
    Class for displaying victory menu
    """
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.name = str()
        self.to_highscore = False
        self.highscore = HighScore(self.surface)

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 60)

    def goto_highscore(self):
        self.highscore.draw()

    def check_inputs(self, events):
        """
        Get inputs to save given name
        :param events:
        :return:
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.highscore.add(self.name, self.player.coins, self.player.enemies_killed)
                    self.highscore.load()
                    self.to_highscore = True
                elif 65 <= event.key <= 122:
                    self.name += chr(event.key)

    def draw(self, events):
        """
        Displays end-game message with player's statistics
        :return:
        """
        if self.to_highscore:
            self.goto_highscore()
        else:
            self.check_inputs(events)

            self.surface.fill("grey")
            # Message
            surf_won = self.font.render("YOU WON!", True, "red")
            won_rect = surf_won.get_rect(midtop=(screen_width/2, screen_height/5))
            surf_name = self.font.render("Your name:", True, "red")
            name_rect = surf_name.get_rect(midtop=(won_rect.left-20, won_rect.bottom+30))
            # Name input
            surf_input = self.font.render(self.name, True, "red")
            # Highscore
            surf_highscore = self.font.render("Press ENTER to proceed to High scores.", True, "red")
            highscore_rect = surf_highscore.get_rect(midtop=(won_rect.centerx, name_rect.bottom + 300))

            self.surface.blit(surf_won, won_rect)
            self.surface.blit(surf_name, name_rect)
            self.surface.blit(surf_input, (name_rect.right+10, won_rect.bottom+30))
            self.surface.blit(surf_highscore, highscore_rect)