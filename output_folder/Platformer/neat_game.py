import neat
import pickle
from settings import *
from game import Platformer


class Neat:
    """
    Class for implementing NEAT algorithm for Platformer game
    Set generation count to 0
    :param draw: whether to draw Level
    :param config: config for single player NEAT
    :param config_multiple: config for multiple players NEAT
    """
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_DIR)
    config_multiple = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_MULTIPLE_DIR)
    initial_threshold = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_DIR).fitness_threshold
    generation = 0
    draw = DRAW_FLAG
    return_to_initial = False

    def __init__(self, multiple=False):
        """
        :param multiple: whether neat will be used with multiple genomes at once
        """
        self.multiple = multiple

    def restore_treshhold(self):
        """
        Restore threshold we changed in order to terminate neat run
        :return:
        """
        if self.config.fitness_threshold == -50 or self.config_multiple.fitness_threshold == -50:
            self.config.fitness_threshold = Neat.initial_threshold
            self.config_multiple.fitness_threshold = Neat.initial_threshold

    def run_neat(self, load_from_checkpoint=None):
        """
        Runs NEAT and prepares population
        :param load_from_checkpoint: sets a checkpoint to load from
        """
        if load_from_checkpoint:
            p = neat.Checkpointer.restore_checkpoint(load_from_checkpoint)
        else:
            if self.multiple:
                p = neat.Population(self.config_multiple)
            else:
                p = neat.Population(self.config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        # p.add_reporter(neat.Checkpointer(NEAT_CHECKPOINT))

        self.restore_treshhold()
        try:
            if self.multiple:
                winner = p.run(eval_genomes_multiple, GENERATION_AMOUNT * 10)
            else:
                winner = p.run(eval_genomes, GENERATION_AMOUNT)
        except TypeError as exc:
            self.return_to_initial = True

        if not self.return_to_initial:
            with open(WINNER_DIR, "wb") as f:
                pickle.dump(winner, f)

    @staticmethod
    def test_neat(config):
        """
        Tests serialized genome from file
        :param config: config file
        :return:
        """
        with open(WINNER_DIR, "rb") as f:
            winner = pickle.load(f)

        game = Platformer()
        game.test_ai(winner, config)


def eval_genomes(genomes, config):
    """
    Runs game with fitness function for single player. Allows force quit and return to initial screen.
    :param genomes: genome from current generation
    """
    if Neat.return_to_initial:
        pass
    else:
        Neat.generation += 1
        for genome_id, genome in genomes:
            genome.fitness = 0
            game = Platformer(Neat.draw)
            force_quit = game.train_ai(genome, config, genome_id, Neat.generation)
            if force_quit and game.return_to_initial:
                Neat.return_to_initial = True
                config.fitness_threshold = -50
                break
            elif force_quit and not game.return_to_initial:
                quit()


def eval_genomes_multiple(genomes, config):
    """
    Runs game with fitness function for multiple players at once. Allows force quit and return to initial screen.
    :param genomes: all genomes from current GENERATION
    """
    if Neat.return_to_initial:
        pass
    else:
        Neat.generation += 1
        game = Platformer(Neat.draw)
        force_quit = game.train_ai_multiple(genomes, config, Neat.generation)
        if force_quit and game.return_to_initial:
            Neat.return_to_initial = True
            # Only found way to terminate neat run function from outside
            config.fitness_threshold = -50
        elif force_quit and not game.return_to_initial:
            quit()


if __name__ == '__main__':
    neat_run = Neat()
    neat_run.run_neat()
    neat_run.test_neat(neat_run.config)
