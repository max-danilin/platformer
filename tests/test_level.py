import unittest
from unittest.mock import patch, Mock, DEFAULT, PropertyMock, MagicMock
from level import Level, LevelError
from settings import *
from player import Player
import pygame
from tiles import ObjectTile, CoinTile, WideTile


class TestLevelUtils(unittest.TestCase):
    @staticmethod
    def helper_inc():
        i = 0

        def helper():
            nonlocal i
            i += 1
            return i

        return helper

    @staticmethod
    def helper_gen(lst):
        yield from lst

    def setUp(self):
        level_test = {'player': ''}
        gen1 = self.helper_gen([['0']])
        pygame.mixer.init()
        player = Mock(spec=pygame.sprite)
        player.mock_add_spec(spec=['rect', 'direction', 'speed', 'add_internal'])
        with patch.multiple('level', EndGame=DEFAULT, Sky=DEFAULT, Water=DEFAULT, Clouds=DEFAULT):
            with patch('level.utils.import_tileset', Mock(return_value=[0, 1, 2])):
                self.patcher1 = patch('level.pygame.image.load')
                img = self.patcher1.start()
                img.return_value = Mock()
                img().convert_alpha = Mock(side_effect=lambda x=0: x)
                with patch('level.utils.import_csv', Mock(return_value=gen1)):
                    self.level = Level(level_test, None, player, None)
                    self.assertRaises(LevelError, Level, [1, 2], None, player, None)
                self.patcher1.stop()

    def test_preload(self):
        self.assertEqual(len(self.level.preloaded), 7)
        self.assertEqual(self.level.preloaded['terrain'][1], 1)
        self.assertEqual(self.level.preloaded['trees'][3], 0)
        self.assertRaises(LevelError, self.level.load_img, '')
        img = self.patcher1.start()
        inc2 = self.helper_inc()
        img.return_value = Mock()
        img().convert_alpha = Mock(side_effect=lambda x=0: inc2())
        self.assertEqual(self.level.load_img({1: '', 2: ''}), {1: 1, 2: 2})
        self.patcher1.stop()

    def test_create_tiles(self):
        gen2 = self.helper_gen([['0', '1'], ['-1', '2']])
        patcher = patch('level.utils.import_csv', Mock(return_value=gen2))
        patcher.start()
        self.level.level_data = {'terrain': ''}
        self.level.preloaded = {'terrain': ['img1', 'img2', 'img3']}
        self.level.create_tile_group('terrain')
        test_terrain = self.level.terrain_tiles.sprites()
        self.assertEqual(len(test_terrain), 3)
        self.assertEqual(test_terrain[0].image, 'img1')
        self.assertEqual(test_terrain[2].rect.x, tile_size)
        self.assertEqual(test_terrain[2].rect.y, tile_size)
        self.level.level_data = {1: ''}
        self.assertRaises(LevelError, self.level.create_tile_group, 'terrain')
        patcher.stop()

        self.level.level_data = {'terrain': ''}
        with patch('level.utils.import_csv', Mock(return_value=[['0', '1'], ['-1', '2']])):
            self.assertRaises(LevelError, self.level.create_tile_group, 'terrain')
        gen3 = self.helper_gen([1, 2])
        with patch('level.utils.import_csv', Mock(return_value=gen3)):
            with self.assertRaises(LevelError):
                self.level.create_tile_group('terrain')

        m1 = Mock(name='img1')
        m2 = Mock(name='img2')
        m3 = Mock(name='img3')
        mock_imgs = [m1, m2, m3 ]
        gen2 = self.helper_gen([['0', '1'], ['-1', '2']])
        self.level.level_data = {'coins': ''}
        with patch('level.utils.import_csv', Mock(return_value=gen2)):
            with patch('tiles.get_images', Mock(return_value=[mock_imgs])):
                self.level.preloaded = {'coins': mock_imgs}
                self.level.create_tile_group('coins')
                test_coins = self.level.objects_tiles.sprites()
                self.assertEqual(len(test_coins), 3)
                self.assertEqual(test_coins[0].image, m1)
                assert isinstance(test_coins[0], CoinTile)

                self.assertEqual(test_coins[1].value, 5)
                self.assertEqual(test_coins[1].image, m2)
                assert isinstance(test_coins[1], ObjectTile)

                self.assertEqual(test_coins[2].hp_recovery, True)
                self.assertEqual(test_coins[2].image, m3)
                assert isinstance(test_coins[2], ObjectTile)

    def tearDown(self):
        pygame.mixer.quit()


class TestLevel(unittest.TestCase):
    def setUp(self):
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.player = Player((0, 0))
        self.patcher = patch.multiple('level', EndGame=DEFAULT, Sky=DEFAULT, Water=DEFAULT, Clouds=DEFAULT)
        self.mocks = self.patcher.start()
        self.level = Level(level_0, self.screen, self.player, Mock())

    def test_scroll(self):
        self.player.rect.centerx = LEFT_SCREEN_EDGE - 1
        self.player.direction.x = -1
        self.player.speed.x = 10
        self.level.scroll_x(self.player)
        self.assertEqual(self.player.speed.x, 0)
        self.assertEqual(self.level.world_shift, 10)

        self.player.rect.centerx = RIGHT_SCREEN_EDGE + 1
        self.player.direction.x = 2
        self.player.speed.x = 20
        self.level.scroll_x(self.player)
        self.assertEqual(self.player.speed.x, 0)
        self.assertEqual(self.level.world_shift, -20)

    def test_gravity(self):
        self.level.apply_gravity(5, self.player)
        self.assertEqual(self.player.direction.y, 5)
        self.assertRaises(LevelError, self.level.apply_gravity, 'str', self.player)

    def test_check_defeat(self):
        self.player.lives = 0
        self.assertTrue(self.level.check_defeat(self.player))
        self.player.lives = 5
        self.player.rect.y = 2000
        self.assertTrue(self.level.check_defeat(self.player))
        self.level.run()
        self.mocks['EndGame']().draw.assert_called_once()

    def test_tree_col(self):
        # Trees: 320, 256/384, 256/3200, 448
        # Falling atop
        self.player.rect.bottom = 250
        self.player.rect.right = 390
        self.player.direction.y = 10
        self.player.update()
        with patch('level.WideTile', Mock(side_effect=WideTile)) as wt:
            # self.level.tree_collision = Mock(side_effect=self.level.tree_collision)
            self.level.tree_collision(self.player, self.level.tree_obs)
            wt.assert_called()
            self.assertTrue(self.player.on_ground)
            self.assertEqual(self.player.rect.bottom, 256)
            self.assertEqual(self.player.direction.y, 0)

        self.player.on_ground = False
        # Colliding from below
        self.player.rect.top = 260
        self.player.rect.right = 360
        self.player.direction.y = -10
        self.player.update()
        with patch('level.WideTile', Mock(side_effect=WideTile)) as wtn:
            self.level.tree_collision(self.player, self.level.tree_obs)
            wtn.assert_not_called()
            self.assertEqual(self.player.rect.top, 250)
            self.assertEqual(self.player.direction.y, -10)

        # Edge 1
        self.player.rect.bottom = 247
        self.player.rect.right = 390
        self.player.direction.y = 10
        self.player.update()
        self.level.tree_collision(self.player, self.level.tree_obs)
        self.assertTrue(self.player.on_ground)
        self.assertEqual(self.player.rect.bottom, 256)
        self.assertEqual(self.player.direction.y, 0)

        self.player.on_ground = False

        # Edge 2
        self.player.rect.bottom = 256
        self.player.rect.right = 390
        self.player.direction.y = 10
        self.player.update()
        self.level.tree_collision(self.player, self.level.tree_obs)
        self.assertTrue(self.player.on_ground)
        self.assertEqual(self.player.rect.bottom, 256)
        self.assertEqual(self.player.direction.y, 0)

        self.player.on_ground = False
        # Colliding from side
        self.player.rect.top = 440
        self.player.rect.left = 3198
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.tree_collision(self.player, self.level.tree_obs)
        self.assertEqual(self.player.rect.left, 3203)
        self.assertEqual(self.player.direction.x, 1)
        self.assertEqual(self.player.rect.y, 440)

    def test_obj_col(self):
        # Coin 271, 360/Apple 1295, 464/Diamond 399, 104 - 5
        # Coin
        self.player.rect.top = 360
        self.player.rect.right = 270
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        n_tiles = len(self.level.objects_tiles.sprites())
        self.level.objects_collision(self.player, self.level.objects_tiles)
        self.assertEqual(self.player.coins, 1)
        self.assertEqual(len(self.level.objects_tiles.sprites()), n_tiles-1)
        self.assertTrue(pygame.mixer.get_busy())

        # Apple
        self.player.rect.bottom = 460
        self.player.rect.left = 1296
        self.player.direction.y = 10
        self.player.update()
        n_tiles = len(self.level.objects_tiles.sprites())
        self.level.objects_collision(self.player, self.level.objects_tiles)
        self.assertEqual(self.player.coins, 1)
        self.assertEqual(self.player.lives, PLAYER_MAX_LIVES+1)
        self.assertEqual(len(self.level.objects_tiles.sprites()), n_tiles - 1)

        self.player.direction.y = 0
        # Diamond
        self.player.rect.top = 104
        self.player.rect.right = 425
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        n_tiles = len(self.level.objects_tiles.sprites())
        self.level.objects_collision(self.player, self.level.objects_tiles)
        self.assertEqual(self.player.coins, 6)
        self.assertEqual(len(self.level.objects_tiles.sprites()), n_tiles - 1)

    def test_enemy_col(self):
        # Enemies 449, 338/833,466
        with patch('level.AFTER_DAMAGE_INVUL', -2):
            self.assertRaises(ValueError, self.level.enemy_collision, self.player, self.level.enemy_tiles)
        with patch('level.AFTER_DAMAGE_INVUL', 'str'):
            self.assertRaises(TypeError, self.level.enemy_collision, self.player, self.level.enemy_tiles)

        # Fall down on enemy
        self.player.rect.bottom = 329
        self.player.rect.left = 449
        self.player.direction.y = 10
        self.player.update()
        self.level.add_explosion_particles = Mock()
        n_enemies = len(self.level.enemy_tiles.sprites())
        n_lives = self.player.lives
        self.level.enemy_collision(self.player, self.level.enemy_tiles)
        self.assertTrue(pygame.mixer.get_busy())
        self.assertEqual(self.player.enemies_killed, 1)
        self.level.add_explosion_particles.assert_called_once()
        self.assertEqual(len(self.level.enemy_tiles.sprites()), n_enemies-1)
        self.assertEqual(self.player.direction.y, -13)
        self.assertEqual(self.player.lives, n_lives)
        pygame.mixer.stop()

        # Collide with enemy from below
        self.player.rect.top = 520
        self.player.rect.left = 833
        self.player.direction.y = -10
        self.player.update()
        self.level.add_explosion_particles = Mock()
        n_lives = self.player.lives
        with patch('level.pygame.time.get_ticks', Mock(return_value=AFTER_DAMAGE_INVUL+1)) as mm:
            self.level.enemy_collision(self.player, self.level.enemy_tiles)
            mm.assert_called_once()
        self.assertEqual(self.player.enemies_killed, 1)
        self.assertTrue(pygame.mixer.get_busy())
        self.level.add_explosion_particles.assert_not_called()
        self.assertEqual(self.player.blinks, 0)
        self.assertEqual(self.player.direction.y, -10)
        self.assertEqual(self.player.lives, n_lives-1)
        pygame.mixer.stop()

        # Collide again right now to check blinking
        self.player.rect.top = 520
        self.player.rect.left = 833
        self.player.direction.y = -10
        self.player.update()
        n_lives = self.player.lives
        self.level.enemy_collision(self.player, self.level.enemy_tiles)
        self.assertEqual(self.player.blinks, 1)
        self.assertFalse(pygame.mixer.get_busy())
        self.assertEqual(self.player.direction.y, -10)
        self.assertEqual(self.player.lives, n_lives)

        # Collision from side
        self.player.rect.top = 460
        self.player.rect.right = 840
        self.player.direction.y = -10
        n_lives = self.player.lives
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        with patch('level.pygame.time.get_ticks', Mock(return_value=AFTER_DAMAGE_INVUL+self.player.last_hit)):
            self.level.enemy_collision(self.player, self.level.enemy_tiles)
        self.assertEqual(self.player.blinks, 0)
        self.assertTrue(pygame.mixer.get_busy())
        self.assertEqual(self.player.direction.y, -10)
        self.assertEqual(self.player.lives, n_lives-1)
        self.assertEqual(self.player.enemies_killed, 1)
        pygame.mixer.stop()

        # Check enemy collision rect, offset=9, no collision
        self.player.rect.top = 460
        self.player.rect.right = 830
        self.player.direction.y = -10
        n_lives = self.player.lives
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        with patch('level.pygame.time.get_ticks', Mock(return_value=AFTER_DAMAGE_INVUL + self.player.last_hit)):
            self.level.enemy_collision(self.player, self.level.enemy_tiles)
        self.assertFalse(pygame.mixer.get_busy())
        self.assertEqual(self.player.lives, n_lives)
        self.assertEqual(self.player.enemies_killed, 1)

    def test_collision(self):
        # Tiles 832, 192/ 896, 192/768, 192
        # Colliding from atop
        self.player.on_ground = False
        self.player.rect.bottom = 190
        self.player.rect.left = 830
        self.player.direction.y = 10
        self.level.check_state(self.player)
        self.assertEqual(self.player.state, 'jump')
        self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.level.check_state(self.player)
        self.assertEqual(self.player.state, 'idle')
        self.level.particle_create(self.player)
        self.assertEqual(len(self.level.particles.sprites()), 1)
        self.assertEqual(self.level.particles.sprites()[0].state, 'land')
        self.assertEqual(self.player.on_ground, True)
        self.assertEqual(self.player.rect.bottom, 192)
        self.assertEqual(self.player.direction.y, 0)
        self.assertEqual(self.player.rect.left, 830)

        # Colliding from below
        self.player.on_ground = False
        self.player.rect.top = 260
        self.player.rect.left = 830
        self.player.direction.y = -10
        self.player.update()
        self.level.check_state(self.player)
        self.assertEqual(self.player.state, 'jump')
        self.level.particle_create(self.player)
        self.assertEqual(len(self.level.particles.sprites()), 2)
        self.assertEqual(self.level.particles.sprites()[1].state, 'jump')
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 256)
        self.assertEqual(self.player.direction.y, 0)
        self.assertEqual(self.player.rect.left, 830)

        # Colliding from below Edge 1
        self.player.on_ground = False
        self.player.rect.top = 256
        self.player.rect.left = 830
        self.player.direction.y = -10
        self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 256)
        self.assertEqual(self.player.direction.y, 0)
        self.assertEqual(self.player.rect.left, 830)

        # Colliding from below Edge 2
        self.player.on_ground = False
        self.player.rect.top = 265
        self.player.rect.left = 830
        self.player.direction.y = -10
        self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 256)
        self.assertEqual(self.player.direction.y, 0)
        self.assertEqual(self.player.rect.left, 830)

        # Colliding from side Edge 1
        self.player.on_ground = False
        self.player.rect.top = 185
        self.player.rect.left = 896
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.direction.x, -1)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 185)
        self.assertEqual(self.player.rect.left, 896)

        # Colliding from side Edge 2
        self.player.on_ground = False
        self.player.rect.top = 185
        self.player.rect.left = 900
        mocked_keys = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.direction.x, -1)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 185)
        self.assertEqual(self.player.rect.left, 896)

        # Colliding diagonal 768, 192 X collision
        self.player.on_ground = False
        self.player.rect.top = 185
        self.player.rect.right = 765
        self.player.direction.y = 10
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.assertEqual(self.player.direction.x, 1)
        self.assertEqual(self.player.on_ground, False)
        self.assertEqual(self.player.rect.top, 195)
        self.assertEqual(self.player.rect.right, 768)
        self.assertEqual(self.player.direction.y, 10)

        # Colliding diagonal 768, 192 no X collision
        self.player.state = 'jump'
        self.player.on_ground = False
        self.player.rect.top = 185
        self.player.rect.right = 769
        self.player.direction.y = 10
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.collision_x_handler(self.player, self.level.terrain_tiles)
        self.level.collision_y_handler(self.player, self.level.terrain_tiles)
        self.level.check_state(self.player)
        self.assertEqual(self.player.state, 'run')
        self.level.particle_create(self.player)
        self.assertEqual(len(self.level.particles.sprites()), 3)
        self.assertEqual(self.level.particles.sprites()[2].state, 'land')
        self.assertEqual(len(self.level.run_particles.sprites()), 1)
        self.assertEqual(self.player.direction.x, 1)
        self.assertEqual(self.player.on_ground, True)
        self.assertEqual(self.player.rect.bottom, 192)
        self.assertEqual(self.player.rect.right, 774)
        self.assertEqual(self.player.direction.y, 0)

        # Test run particle
        self.level.particle_draw(self.player, self.level.particles, self.level.run_particles)
        sprite = self.level.run_particles.sprite
        self.assertEqual(sprite.rect.x, self.player.rect.x-10)
        self.assertEqual(sprite.rect.y, self.player.rect.bottom - 10)
        self.assertFalse(sprite.flipped_flag)
        self.player.state = 'idle'
        self.level.particle_draw(self.player, self.level.particles, self.level.run_particles)
        self.assertEqual(len(self.level.run_particles.sprites()), 0)


    def test_enemy_constr(self):
        # Enemy 2048, 210/constr 1920, 192
        enemy = self.level.enemy_tiles.sprites()[0]
        enemy.rect.left = 1867
        enemy.enemy_speed = 5
        old_speed = enemy.enemy_speed
        old_flag = enemy.flipped_flag
        enemy.update(0)
        self.level.enemy_constrains(enemy, self.level.constrains)
        self.assertEqual(enemy.enemy_speed, -old_speed)
        self.assertEqual(enemy.flipped_flag, not old_flag)

        enemy.rect.left = 1986
        old_speed = enemy.enemy_speed
        old_flag = enemy.flipped_flag
        enemy.update(0)
        self.level.enemy_constrains(enemy, self.level.constrains)
        self.assertEqual(enemy.enemy_speed, -old_speed)
        self.assertEqual(enemy.flipped_flag, not old_flag)

    def test_level_finish(self):
        # Tile 3776 192
        self.player.rect.top = 185
        self.player.rect.right = 3775
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.player.update()
        self.level.level_finish(self.player, self.level.level_end)
        self.assertTrue(self.level.completed)
        self.assertEqual(self.player.levels_completed, 1)

    def test_return_and_restore(self):
        pygame.mixer.stop()
        mocked_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_BACKSPACE: True}
        with patch('player.pygame.key.get_pressed', return_value=mocked_keys):
            self.level.return_to_menu(self.player)
            self.assertTrue(self.level.back_to_menu)
            self.assertTrue(self.level.postponed)
            self.level.start_music()
            self.assertTrue(pygame.mixer.get_busy())
            self.level.restore_player(self.player)
            self.assertFalse(self.level.postponed)
            self.assertEqual((self.player.rect.x, self.player.rect.y), self.player.pps[0])

    def tearDown(self):
        self.patcher.stop()
        pygame.mixer.quit()
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
