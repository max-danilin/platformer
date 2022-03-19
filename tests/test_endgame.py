import unittest
from endgame import EndGame
from unittest.mock import Mock
import pygame
from settings import screen_height, screen_width


class TestEndgame(unittest.TestCase):
    def test_endgame(self):
        surface = pygame.display.set_mode((screen_width, screen_height))
        player = Mock()
        player.coins = 1
        player.levels_completed = 0
        player.enemies_killed = 100
        pygame.mixer.init()
        endgame = EndGame(surface, player)
        endgame.play_sound()
        self.assertTrue(pygame.mixer.get_busy())
        self.assertEqual(endgame.draw(), None)
        pygame.mixer.quit()
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
