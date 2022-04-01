import unittest
from unittest.mock import patch, Mock
from neat_game import Neat


class TestNeat(unittest.TestCase):
    def test_run(self):
        neat = Neat()
        Neat.return_to_initial = True
        with patch('neat_game.eval_genomes') as m:
            neat.run_neat()
            m.assert_called()
        neat.multiple = True
        with patch('neat_game.eval_genomes_multiple') as mm:
            neat.run_neat()
            mm.assert_called()

    def test_return(self):
        neat_run = Neat()
        Neat.generation = 0
        Neat.return_to_initial = False
        with patch('neat_game.Platformer') as m:
            mm = Mock(return_value=True)
            m().train_ai = mm
            m().return_to_initial = True
            neat_run.run_neat()
            self.assertEqual(neat_run.config.fitness_threshold, -50)
            self.assertTrue(neat_run.return_to_initial)
            neat_run.restore_treshhold()
            self.assertEqual(neat_run.config.fitness_threshold, 5000)
            self.assertEqual(neat_run.generation, 1)

    def test_multiple(self):
        neat_run = Neat(multiple=True)
        Neat.generation = 0
        Neat.return_to_initial = False
        with patch('neat_game.Platformer') as m:
            mm = Mock(return_value=True)
            m().train_ai_multiple = mm
            m().return_to_initial = True
            neat_run.run_neat()
            self.assertEqual(neat_run.config_multiple.fitness_threshold, -50)
            self.assertTrue(neat_run.return_to_initial)
            neat_run.restore_treshhold()
            self.assertEqual(neat_run.config_multiple.fitness_threshold, 5000)
            self.assertEqual(neat_run.generation, 1)


