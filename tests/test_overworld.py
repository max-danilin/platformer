import unittest
from unittest.mock import patch, Mock, DEFAULT
from overworld import Overworld
import pygame
from player import Player
from settings import *


class TestOverworld(unittest.TestCase):
    test_dict = {'level_0': {'name': 'lvl0', 'pos': (20, 20), 'level': {1: '1', 2: '2'}},
                 'level_1': {'name': 'lvl1', 'pos': (200, 200), 'level': {1: '11', 2: '22'}, 'activate': False,
                             'for_activation': ('lvl0',)}}

    def setUp(self):
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        with patch.multiple('overworld', Victory=DEFAULT, UI=DEFAULT, Sky=DEFAULT):
            mock = Mock()
            self.player = Player((0, 0))
            with patch('overworld.level_bricks', self.test_dict):
                img_mock = Mock()
                with patch('brick_level.pygame.image.load') as m:
                    m().convert_alpha = img_mock
                    active_mock = Mock()
                    img_mock().copy = Mock(return_value=active_mock)
                    mm = Mock(return_value=pygame.Rect(20, 20, 80, 80))
                    active_mock.get_rect = mm
                    self.over = Overworld(mock, self.player)

    def test_creation(self):
        self.assertEqual(len(self.over.brick_levels.sprites()), 2)
        self.assertEqual(len(self.over.players.sprites()), 1)
        self.assertEqual(self.over.players.sprite.rect.center, (60, 60))

    def test_start(self):
        bricks = self.over.brick_levels.sprites()
        self.over.set_state()
        self.assertTrue(self.over.started)
        self.assertTrue(pygame.mixer.get_busy())
        self.assertIn(bricks[0].rect.center, self.over.ava_points)
        self.assertIn(bricks[0], self.over.ava_bricks)
        self.assertFalse(bricks[1].activate)
        self.assertEqual(self.player.direction.x, 0)
        self.assertEqual(self.player.direction.y, 0)
        bricks[0].completed = True
        self.over.check_level_activation()
        self.assertTrue(bricks[1].activate)
        self.over.check_available()
        self.assertIn(bricks[1].rect.center, self.over.ava_points)
        self.assertIn(bricks[1], self.over.ava_bricks)

    def test_movement(self):
        bricks = self.over.brick_levels.sprites()
        bricks[0].rect = pygame.Rect(*self.test_dict['level_0']['pos'], 80, 80)
        bricks[1].rect = pygame.Rect(*self.test_dict['level_1']['pos'], 80, 80)
        self.over.points = [brick.rect.center for brick in bricks]
        self.player.rect.center = self.over.points[0]
        self.over.check_available()

        # Moving along equation
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.rect.centery, 65)
        self.assertEqual(self.over.check_position(self.player), bricks[0])
        mocked_keys = {pygame.K_RETURN: True}
        with patch('overworld.pygame.key.get_pressed', return_value=mocked_keys):
            self.over.go_to_level()
            self.assertEqual(self.over.proceed_to_level, bricks[0])
        self.assertFalse(self.over.check_victory())

        # Moving just along X
        self.player.rect.center = (60, 60)
        self.player.direction.x = 0
        self.player.speed.x = 10
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.rect.center, (50, 60))
        self.assertEqual(self.player.rect.midleft, (23, 60))
        self.assertEqual(self.over.check_position(self.player), bricks[0])

        # Reaching left restraint
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.rect.midleft, (20, 60))
        self.assertEqual(self.over.check_position(self.player), bricks[0])

        # Reaching right restraint
        self.player.rect.center = (60, 60)
        self.player.direction.x = 0
        self.player.speed.x = 30
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.direction.x, 0)
        self.assertEqual(self.player.direction.y, 0)
        self.assertEqual(self.player.rect.midright, (100, 90))
        self.assertEqual(self.over.check_position(self.player), bricks[0])
        bricks[0].completed = True
        mocked_keys = {pygame.K_RETURN: True}
        with patch('overworld.pygame.key.get_pressed', return_value=mocked_keys):
            self.over.go_to_level()
            self.assertEqual(self.over.compl_brick, bricks[0])
            blit_mock = Mock()
            self.over.surface.blit = blit_mock
            self.over.completed_level(self.over.compl_brick)
            blit_mock.assert_called_once()
        self.assertFalse(self.over.check_victory())

        # Moving along equation to next point
        bricks[1].activate = True
        self.over.check_available()
        self.player.rect.center = (60, 60)
        self.player.direction.x = 0
        self.player.speed.x = 60
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.rect.center, (120, 120))
        self.assertEqual(self.over.check_position(self.player), None)
        self.over.compl_brick = None
        self.over.proceed_to_level = None
        mocked_keys = {pygame.K_RETURN: True}
        with patch('overworld.pygame.key.get_pressed', return_value=mocked_keys):
            self.over.go_to_level()
            self.assertEqual(self.over.compl_brick, None)
            self.assertEqual(self.over.proceed_to_level, None)

        # Reaching next point
        self.player.direction.x = 0
        self.player.speed.x = 90
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.over.player_movement(self.player)
        self.over.player_constraints(self.player, self.over.ava_bricks)
        self.assertEqual(self.player.rect.center, (210, 210))
        self.assertEqual(self.over.check_position(self.player), bricks[1])
        self.over.player_set_animation(self.player)
        self.assertEqual(self.player.state, 'run')
        mocked_keys = {pygame.K_RETURN: True}
        with patch('overworld.pygame.key.get_pressed', return_value=mocked_keys):
            self.over.go_to_level()
            self.assertEqual(self.over.proceed_to_level, bricks[1])
        bricks[1].completed = True
        self.assertTrue(self.over.check_victory())

    def tearDown(self):
        pygame.mixer.quit()
        pygame.display.quit()


class TestDrawing(unittest.TestCase):
    test_dict = {'level_0': {'name': 'lvl0', 'pos': (20, 20), 'level': {1: '1', 2: '2'}},
                 'level_1': {'name': 'lvl1', 'pos': (200, 200), 'level': {1: '11', 2: '22'}, 'activate': False,
                             'for_activation': ('lvl0',)},
                 'level_2': {'name': 'lvl2', 'pos': (380, 20), 'level': {1: '1', 2: '2'}, 'activate': False}}

    def setUp(self):
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill('white')
        with patch.multiple('overworld', Victory=DEFAULT, UI=DEFAULT, Sky=DEFAULT):
            self.player = Player((0, 0))
            with patch('overworld.level_bricks', self.test_dict):
                img_mock = Mock()
                with patch('brick_level.pygame.image.load') as m:
                    m().convert_alpha = img_mock
                    active_mock = Mock()
                    img_mock().copy = Mock(return_value=active_mock)
                    mm = Mock(return_value=pygame.Rect(20, 20, 80, 80))
                    active_mock.get_rect = mm
                    self.over = Overworld(self.screen, self.player)

    def test_draw_lines(self):
        bricks = self.over.brick_levels.sprites()
        bricks[0].rect = pygame.Rect(*self.test_dict['level_0']['pos'], 80, 80)
        bricks[1].rect = pygame.Rect(*self.test_dict['level_1']['pos'], 80, 80)
        bricks[2].rect = pygame.Rect(*self.test_dict['level_2']['pos'], 80, 80)
        self.over.points = [brick.rect.center for brick in bricks]

        self.over.check_available()
        self.over.draw_lines()
        self.assertEqual(self.screen.get_at((150, 150)), (0, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 150)), (0, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 60)), (255, 255, 255, 255))

        bricks[1].activate = True
        self.over.check_available()
        self.over.draw_lines()
        self.assertEqual(self.screen.get_at((150, 150)), (255, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 150)), (0, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 60)), (255, 255, 255, 255))

        bricks[2].activate = True
        self.over.check_available()
        self.over.draw_lines()
        self.assertEqual(self.screen.get_at((150, 150)), (255, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 150)), (255, 0, 0, 255))
        self.assertEqual(self.screen.get_at((330, 60)), (255, 255, 255, 255))

    def tearDown(self):
        pygame.mixer.quit()
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
