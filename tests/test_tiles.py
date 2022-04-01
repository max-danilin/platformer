import unittest
from unittest.mock import patch, Mock
import tiles
from settings import ANIMATION_SPEED, ENEMY_SPEED
from pygame import Surface


class TestTiles(unittest.TestCase):
    def test_tile(self):
        self.assertRaises(ValueError, tiles.Tile, -1, (10, 10))
        tile = tiles.Tile(1, (0, 0))
        tile.update(3)
        self.assertEqual(tile.rect.x, 3)
        self.assertRaises(TypeError, tile.update, 'str')

    def test_animated(self):
        animated = tiles.AnimatedTile(2, (0, 0), 1)
        animated.update(3)
        self.assertEqual(animated.frame_index, 0)
        animated.animated = True
        animated.images = [0, 1, 2]
        animated.update(3)
        self.assertEqual(animated.rect.x, 6)
        self.assertEqual(animated.frame_index, ANIMATION_SPEED)
        self.assertEqual(animated.image, 0)
        animated.frame_index = 1
        animated.update(3)
        self.assertEqual(animated.image, 1)
        animated.frame_index = 5
        animated.update(3)
        self.assertEqual(animated.image, 0)
        with patch('tiles.ANIMATION_SPEED', 'str'):
            self.assertRaises(TypeError, tiles.AnimatedTile, 2, (0, 0), 1)

    def test_enemy(self):
        srf = Surface((2, 2))
        srf_flip = Surface((5, 5))
        with patch('tiles.get_enemy_images', Mock(return_value=[srf, 1, 2])):
            with patch('tiles.pygame.transform.flip', Mock(return_value=srf_flip)):
                enemy = tiles.EnemyTile(2, (0, 0), 1)
                enemy.images = tiles.get_enemy_images()
                enemy.update(3)
                self.assertEqual(enemy.image, srf_flip)
                self.assertEqual(enemy.rect.x, 3+ENEMY_SPEED)
                enemy.frame_index = 1
                enemy.flipped_flag = False
                enemy.update(3)
                self.assertEqual(enemy.image, 1)
                self.assertEqual(enemy.rect.x, 2*(3+ENEMY_SPEED))
                with patch('tiles.ENEMY_SPEED', 'str'):
                    self.assertRaises(TypeError, tiles.EnemyTile, 2, (0, 0), 1)


if __name__ == '__main__':
    unittest.main()
