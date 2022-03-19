import unittest
import utils
from unittest.mock import patch
import pygame
from unittest.mock import Mock


class TestUtils(unittest.TestCase):
    def test_get_img(self):
        self.assertRaises(TypeError, utils.get_img, '', 123)
        with patch('utils.pygame.image.load'):
            test_states = utils.get_img("tests/test_img_states", {'idle': []})
            self.assertEqual(len(test_states['idle']), 1)

    def test_import_tileset(self):
        self.assertRaises(FileNotFoundError, utils.import_tileset, '')
        self.screen = pygame.display.set_mode((200, 200))
        test_tiles = utils.import_tileset("tests/test_tileset/setup_tile.png")
        self.assertEqual(len(test_tiles), 2)
        self.assertEqual(test_tiles[1].get_rect().width, 64)
        test_tiles2 = utils.import_tileset("tests/test_tileset/1.png")
        self.assertEqual(len(test_tiles2), 2)
        self.assertEqual(test_tiles2[1].get_rect().width, 64)
        pygame.display.quit()

    def test_load_flipped(self):
        self.assertRaises(TypeError, utils.load_flipped, '')
        self.assertRaises(TypeError, utils.load_flipped, {'idle': 1})
        self.assertRaises(TypeError, utils.load_flipped, {'idle': [1,]})


if __name__ == '__main__':
    unittest.main()
