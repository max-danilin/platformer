import unittest
from unittest.mock import patch, Mock, DEFAULT
from initial_screen import Button, InitialScreen
import pygame
from settings import *


class TestInitial(unittest.TestCase):
    def test_button(self):
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        mock_render = Mock()
        b = Button(self.screen, (0, 0), (10, 10), mock_render, 'some\ntext')
        self.assertTrue(b.multiple_text)
        self.assertEqual(len(b.render_list), 2)
        mock_render.render.assert_called_with('text', True, BUTTON_TEXT_COLOR)
        with patch('initial_screen.pygame.mouse.get_pressed') as m:
            m.return_value = [True]
            pygame.mouse.get_pos = Mock(return_value=(5, 5))
            with patch('initial_screen.pygame.draw'):
                b.render_list = []
                b.initial_text_y = (0,)
                b.draw()
                self.assertTrue(b.pressed)
                self.assertEqual(b.rect_list[0].y, BUTTON_ELEVATION)
                self.assertEqual(b.sound_timeout, 1)

                m.return_value = [False]
                b.draw()
                self.assertFalse(b.pressed)
                self.assertEqual(b.upper.y, b.initial_y)

                pygame.mouse.get_pos = Mock(return_value=(15, 15))
                b.draw()
                self.assertFalse(b.pressed)
                self.assertFalse(b.was_pressed)
                self.assertEqual(b.upper.y, b.initial_y)
                self.assertEqual(b.sound_timeout, 3)

                m.return_value = [True]
                b.draw()
                self.assertFalse(b.pressed)
                self.assertTrue(b.was_pressed)
                self.assertEqual(b.upper.y, b.initial_y)

                pygame.mouse.get_pos = Mock(return_value=(5, 5))
                b.draw()
                self.assertFalse(b.pressed)
                self.assertTrue(b.was_pressed)
                self.assertEqual(b.upper.y, b.initial_y)
                self.assertEqual(b.sound_timeout, 5)

        pygame.mixer.quit()
        pygame.display.quit()

    def test_screen(self):
        with patch('initial_screen.pygame.image.load') as m:
            m().convert = Mock()
            with patch('initial_screen.pygame.transform.scale'):
                with patch('initial_screen.pygame.time.Clock'):
                    screen = InitialScreen()
                    assert isinstance(screen.neat, Button)
                    self.assertEqual(len(screen.buttons), 3)

                    screen.rect.x = 0
                    screen.rect.right = screen_width
                    screen.image_for_loop = pygame.Surface((10, 10))
                    screen.rect_for_loop = pygame.Rect((0, 0), (10, 10))
                    screen.animate()
                    self.assertEqual(screen.rect.x, -BACK_ANIMATION_SPEED)
                    self.assertEqual(screen.rect_for_loop.x, -BACK_ANIMATION_SPEED)

                    screen.rect.right = 0
                    screen.animate()
                    self.assertEqual(screen.rect.x, 0)
                    self.assertEqual(screen.rect_for_loop.x, screen_width)

                    with patch.multiple('initial_screen', Neat=DEFAULT, Platformer=DEFAULT) as mocks:
                        mocks['Neat'].return_to_initial = True
                        screen.set_mode('neat')
                        self.assertTrue(screen.initial_run)
                        mocks['Neat']().run_neat.assert_called()

                        mocks['Platformer']().return_to_initial = True
                        screen.set_mode('game')
                        self.assertTrue(screen.initial_run)
                        mocks['Platformer']().run.assert_called()

        pygame.mixer.quit()
        pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
