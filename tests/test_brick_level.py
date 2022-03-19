import unittest
from unittest.mock import patch, Mock
from brick_level import LevelBrick
from settings import *


class TestBrickLevel(unittest.TestCase):
    def test_brick(self):
        with patch('brick_level.pygame.image.load') as m:
            self.assertRaises(TypeError, LevelBrick, 12, (1, 1), level_0)
            self.assertRaises(TypeError, LevelBrick, 'sfd', (1, 1), [1, 2])
            self.assertRaises(TypeError, LevelBrick, 'sfd', (0, 0), {1: '', 2: ''}, for_activation='lvl')
            brick_level = LevelBrick('level_0', (0, 0), {1: '', 2: ''})
            m.assert_called()

            al = Mock()
            with patch('brick_level.Level', Mock(return_value=al)) as mm:
                mock = Mock()
                brick_level.run_level(mock, mock, mock)
                mm.assert_called_once_with(level_bricks['level_0']['level'], mock, mock, mock)
                al.completed = True
                brick_level.run_level(mock, mock, mock)
                self.assertTrue(brick_level.completed)
                self.assertTrue(brick_level.stop_level)
                brick_level.stop_level = False
                al.completed = False
                al.back_to_menu = True
                brick_level.run_level(mock, mock, mock)
                self.assertTrue(brick_level.stop_level)
                self.assertFalse(al.back_to_menu)

            brick_level.inactive = Mock(name='inactive')
            self.assertNotEqual(brick_level.image, brick_level.inactive)
            brick_level.activate = False
            brick_level.is_activated()
            self.assertEqual(brick_level.image, brick_level.inactive)

            brick_level.image.blit = Mock(name='blit')
            brick_level.completed = True
            brick_level.is_completed()
            brick_level.image.blit.assert_called_once_with(brick_level.check_sign, (10, 40))


if __name__ == '__main__':
    unittest.main()
