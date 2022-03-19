import unittest
from unittest.mock import Mock
from victory import Victory
from collections import namedtuple
import pygame
from settings import *


class TestVictory(unittest.TestCase):
    def test_victory(self):
        surface = Mock()
        player = Mock()
        victory = Victory(surface, player)
        victory.highscore = Mock()
        Event = namedtuple('Event', 'type, key')
        events = [Event(pygame.KEYDOWN, 116), Event(pygame.KEYDOWN, 101),
                  Event(pygame.KEYDOWN, 115), Event(pygame.KEYDOWN, 116), Event(pygame.KEYDOWN, pygame.K_RETURN)]
        victory.check_inputs(events)
        self.assertEqual(victory.name, 'test')
        self.assertEqual(victory.to_highscore, True)

    def test_draw(self):
        screen = pygame.display.set_mode((screen_width, screen_height))
        Event = namedtuple('Event', 'type, key')
        events = [Event(pygame.KEYDOWN, 116), Event(pygame.KEYDOWN, 101),
                  Event(pygame.KEYDOWN, 115), Event(pygame.KEYDOWN, 116), Event(pygame.KEYDOWN, pygame.K_RETURN)]
        victory = Victory(screen, Mock())
        victory.highscore = Mock()
        self.assertEqual(victory.draw(events), None)
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
