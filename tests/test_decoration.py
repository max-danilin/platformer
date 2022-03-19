import unittest
from unittest.mock import patch, Mock
from decoration import *
from random import seed
from settings import *
import pygame


class TestDecoration(unittest.TestCase):
    @staticmethod
    def helper_inc():
        i = 0

        def helper():
            nonlocal i
            i += 1
            return i
        return helper

    def test_clouds(self):
        inc = self.helper_inc()
        seed(0)
        with patch('decoration.glob.glob', Mock(return_value=range(10))):
            with patch('decoration.pygame.image.load') as cloud_mock:
                cloud_mock.return_value = Mock()
                cloud_mock().convert_alpha = Mock(side_effect=inc)
                cloud = Clouds(10, 10, 10)
                self.assertEqual(len(cloud.cloud_sprites.sprites()), 10)
                fst_sprite = cloud.cloud_sprites.sprites()[0]
                self.assertEqual(fst_sprite.image, 7)
                self.assertIn(fst_sprite.rect.y, range(0, 11))
                self.assertRaises(ValueError, Clouds, 10, -1, 0)
                self.assertRaises(TypeError, Clouds, 'str', '1', '2')

    def test_water(self):
        with patch('decoration.pygame.image.load'):
            with patch('decoration.get_tile_img'):
                water = Water(10, 10)
                amount = (10 + 2 * screen_width) // WATER_TILE_WIDTH
                self.assertEqual(len(water.water_sprites.sprites()), amount)
                self.assertRaises(ValueError, Water, 10, -1,)
                self.assertRaises(TypeError, Water, 'str', '1')

    def test_sky(self):
        screen = pygame.display.set_mode((screen_width, screen_height))
        sky = Sky(10)
        self.assertEqual(sky.draw(screen), None)
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
