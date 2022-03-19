import unittest
from ui import UI
from unittest.mock import patch, Mock
import pygame
from settings import *


class TestUI(unittest.TestCase):
    def test_ui(self):
        screen = Mock()
        player = Mock()
        player.lives = 5
        player.max_lives = 5
        with patch('ui.pygame.image.load'):
            ui = UI(screen, player)
            rect = ui.get_current_hp()
            self.assertEqual(rect.width, ui.hb_width)

            player.lives = 10
            player.max_lives = 5
            rect = ui.get_current_hp()
            self.assertEqual(rect.width, ui.hb_width)

            player.lives = 1
            player.max_lives = 2
            rect = ui.get_current_hp()
            self.assertEqual(rect.width, ui.hb_width/2)
            with patch('ui.HELTH_BAR_POS', 12):
                self.assertRaises(TypeError, UI, screen, player)

    def test_draw(self):
        screen = pygame.display.set_mode((screen_width, screen_height))
        player = Mock()
        player.lives = 5
        player.max_lives = 5
        player.coins = 10
        ui = UI(screen, player)
        self.assertEqual(ui.draw(), None)
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
