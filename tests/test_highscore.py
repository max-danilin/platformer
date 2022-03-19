import unittest
from highscore import HighScore
from unittest.mock import patch, Mock, mock_open
import hashlib
from settings import HASH_KEY, screen_height, screen_width
import pygame


class TestHighscore(unittest.TestCase):
    def test_highscore(self):
        surface = pygame.display.set_mode((screen_width, screen_height))
        highscore = HighScore(surface)
        self.assertRaises(TypeError, highscore.add, 12, 12, 12)
        self.assertRaises(TypeError, highscore.add, 'Max', 'max', 12)
        self.assertRaises(TypeError, highscore.add, 'Max', 12, [1, ])
        m = mock_open()
        with patch('highscore.open', m):
            highscore.add('max', 10, 10)
            hash = hashlib.blake2b(str('max' + str(10) + HASH_KEY).encode('utf-8')).hexdigest()
            handle = m()
            str_hash = 'max' + "[::]" + str(10) + "[::]" + str(10) + "[::]" + str(hash) + "\n"
            handle.write.assert_called_with(str_hash)
        with patch('highscore.open', mock_open(read_data=str_hash)):
            highscore.load()
            self.assertEqual(highscore.highscores[0], ['max', 10, 10])
        self.assertEqual(highscore.draw(), None)
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
