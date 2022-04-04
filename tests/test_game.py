import unittest
from unittest.mock import Mock, patch
from game import Platformer
from neat_game import Neat, eval_genomes, eval_genomes_multiple
import pygame
from collections import namedtuple


class TestGame(unittest.TestCase):
    def test_game(self):
        with patch('game.pygame.time.Clock'):
            game = Platformer(draw=True)
            game.overworld.proceed_to_level = None
            game.overworld.check_victory = Mock(return_value=True)
            game.overworld.run = Mock(side_effect=game.overworld.run)
            events = namedtuple('events', 'type, key')
            mocked_keys = [events(pygame.KEYDOWN, pygame.K_BACKSPACE)]
            with patch('game.pygame.event.get', return_value=mocked_keys):
                game.run()
                game.overworld.run.assert_called_with(mocked_keys)
                pygame.mixer.quit()
                pygame.display.quit()

    def test_neat(self):
        with patch('game.pygame.time.Clock'):
            neat_run = Neat()
            with patch('neat_game.Platformer') as plat:
                plat.side_effect = Platformer
                plat().train_ai = Mock(side_effect=Platformer.train_ai, return_value=True)
                events = namedtuple('events', 'type, key')
                mocked_keys = [events(pygame.KEYDOWN, pygame.K_BACKSPACE)]
                with patch('game.pygame.event.get', return_value=mocked_keys):
                    neat_run.run_neat()
                    plat.assert_called()
                    self.assertEqual(Neat.generation, 1)

            Neat.generation = 0
            Neat.return_to_initial = False
            neat_multiple = Neat(multiple=True)
            with patch('neat_game.Platformer') as plat:
                plat.side_effect = Platformer
                plat().train_ai_multiple = Mock(side_effect=Platformer.train_ai_multiple, return_value=True)
                events = namedtuple('events', 'type, key')
                mocked_keys = [events(pygame.KEYDOWN, pygame.K_BACKSPACE)]
                with patch('game.pygame.event.get', return_value=mocked_keys):
                    neat_multiple.run_neat()
                    plat.assert_called()
                    self.assertEqual(Neat.generation, 1)

            Neat.generation = 0
            Neat.return_to_initial = False


if __name__ == '__main__':
    unittest.main()
