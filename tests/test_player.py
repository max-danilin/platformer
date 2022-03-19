import glob
import os
import unittest
from shutil import rmtree
from unittest.mock import patch, Mock, DEFAULT

import pygame

from maker import refactor_image
from player import Player, PlayerCreationError
from settings import *


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        pygame.mixer.init()
        self.player = Player((0, 0))
        self.player.jump_sound = Mock()

    def test_refactor(self):
        self.assertRaises(ValueError, refactor_image, 0, 2000, glob.glob("tests/test_img_good/*"), ('run',), "tests/test_img_new")
        self.assertRaises(TypeError, refactor_image, 10, 10, "img", ('run',), "tests/test_img_new")
        self.assertRaises(TypeError, refactor_image, 10, 10, glob.glob("tests/test_img_good/*"), 12, "tests/test_img_new")
        self.assertRaises(TypeError, refactor_image, 10, 10, glob.glob("tests/test_img_good/*"), ('run',), 12)
        self.assertRaises(TypeError, refactor_image, 10, 10, glob.glob("tests/test_img/*"), ('idle', 'jump'), "tests/test_img_new")

        refactor_image(10, 10, glob.glob("tests/test_img_good/*"), ('idle', 'jump'), "tests/test_img_new")
        self.assertCountEqual(os.listdir("tests/test_img_new"), ["IDLE_0_mod.png", "JUMP_0_mod.png"])
        rmtree("tests/test_img_new")

    def test_creation(self):
        self.assertEqual(self.player.direction.x, 0)
        self.assertEqual(len(self.player.states['idle']), 10)
        self.assertEqual(len(self.player.flipped['run']), 10)
        self.player.max_lives = -2
        self.assertRaises(PlayerCreationError, self.player.check_parameters)
        m = Mock()
        mock = Mock(get_rect=m)
        m.return_value = pygame.Rect(1, 1, 1, 1)
        with patch.multiple('player', get_img=Mock(return_value={'r': [mock]}), load_flipped=DEFAULT):
            with patch('player.ALL_STATES', 'run'):
                self.assertRaises(PlayerCreationError, Player, (0, 0))
        with patch('player.JUMP_SPEED', 'run'):
            self.assertRaises(PlayerCreationError, Player, (0, 0))
        with patch('player.PLAYER_SPEED', -2):
            self.assertRaises(PlayerCreationError, Player, (0, 0))
        with patch('player.ANIMATION_SPEED', 'run'):
            self.assertRaises(PlayerCreationError, Player, (0, 0))
        with patch('player.BLINKING_DURATION', 'run'):
            self.assertRaises(PlayerCreationError, Player, (0, 0))

    def test_moving(self):
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: True}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.get_inputs = Mock(side_effect=self.player.get_inputs)
            self.player.animate = Mock()
            self.player.update()
            self.player.get_inputs.assert_called()

            self.assertEqual(self.player.direction.x, -1)
            self.assertEqual(self.player.rect.x, -PLAYER_SPEED)
            self.assertEqual(self.player.rect.y, 0)

            self.player.jump()
            self.assertEqual(self.player.direction.y, JUMP_SPEED)
            self.player.jump_sound.play.assert_called_once()

    def test_animation(self):
        self.player.get_inputs = Mock()
        self.player.prev_state = "idle"
        self.player.update()

        self.assertEqual(self.player.frame_index, ANIMATION_SPEED)
        self.player.frame_index = 1
        self.player.update()

        self.assertEqual(self.player.image, self.player.states['idle'][1])
        self.player.frame_index = 10
        self.player.update()

        self.assertEqual(self.player.frame_index, 0)
        self.assertEqual(self.player.image, self.player.states['idle'][0])
        self.player.moving_right = False
        self.player.frame_index = 2
        self.player.state = 'run'
        self.player.update()

        self.assertEqual(self.player.image, self.player.flipped['run'][0])
        self.player.prev_state = "jump"
        self.player.state = 'jump'
        self.player.frame_index = len(self.player.states['jump']) - 1
        self.player.update()

        self.assertEqual(self.player.image, self.player.flipped['jump'][9])

    def test_blinking(self):
        self.player.blinks = 0
        self.player.update()

        self.assertEqual(self.player.image.get_alpha(), 0)
        self.assertEqual(self.player.blinks, 1)
        self.assertEqual(self.player.states['idle'][0].get_alpha(), 0)
        self.player.update()

        self.assertEqual(self.player.states['idle'][0].get_alpha(), 255)
        self.assertEqual(self.player.blinks, 2)
        self.assertEqual(self.player.image.get_alpha(), 255)

    def tearDown(self):
        pygame.display.quit()
        pygame.mixer.quit()


if __name__ == '__main__':
    unittest.main()
