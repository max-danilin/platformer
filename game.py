import pygame
import sys
from settings import *
from overworld import Overworld
from player import Player
from ui import UI
from level import Level
from collections import deque
import neat
import pickle
import level_old

# TODO Maybe try data analysis based on ai behaviour


class Platformer:  # TODO Add initial screen with buttons
    """
    Main class for the game with main loop

    Use Python 3.7
    """
    def __init__(self):  # TODO Refactor
        """
        Initializing pygame, creating player and overworld
        """
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.frame = 0
        pygame.mixer.init()

        self.player = Player((0, 0))
        self.overworld = Overworld(self.screen, self.player)

        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).set_volume(0.05)

    @staticmethod
    def process_events():
        """
        Process occuring events and return them
        :return:
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        return events

    @staticmethod
    def fitness(frames, distance, score, win, enemy_kills, defeat):
        frames = (frames // 60)
        distance = int(distance//64)
        if distance < 0:
            distance = 0
        return distance ** 2 - frames ** 1.5 + score ** 1.5 + enemy_kills * 20 + min(max(distance - 20, 0), 1) * 2000 \
               + win * 10000 - defeat * 50

    def run(self):
        """
        Main game function
        :return:
        """
        while True:
            events = self.process_events()

            self.screen.fill('grey')
            self.overworld.run(events)

            pygame.display.update()
            self.clock.tick(60)

    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        player = Player((0, 0), neat=True)
        ui = UI(self.screen, player)
        l_neat = Level(level_0, self.screen, player, ui, neat=True)

        while True:
            self.process_events()

            self.screen.fill('grey')
            l_neat.run()
            if l_neat.completed:
                print("You win!")
                quit()
            output = net.activate(l_neat.nparray_to_list())
            decision = output.index(max(output))

            if decision == 0:
                pass
            elif decision == 1:
                l_neat.move_up()
            elif decision == 2:
                l_neat.move_right()
            elif decision == 3:
                l_neat.move_left()
            elif decision == 4:
                l_neat.move_right_up()
            elif decision == 5:
                l_neat.move_left_up()

            pygame.display.update()
            self.clock.tick(60)

    def train_ai(self, genome, config):  # TODO Try adding opportunity for creating multiple players simultaneously
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        player = Player((0, 0), neat=True)
        ui = UI(self.screen, player)
        l_neat = Level(level_0, self.screen, player, ui, neat=True)
        queue = deque(maxlen=200)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return True

            self.screen.fill('grey')
            l_neat.run()
            dist = l_neat.distance_traveled(player)
            fitness = self.fitness(
                self.frame, dist, player.coins, l_neat.completed,
                player.enemies_killed, l_neat.check_defeat(player)
            )

            queue.append(dist)
            if len(queue) == 200:
                deq = queue
            else:
                deq = deque([1, 100])
            if deq[-1] - deq[0] < 11 or l_neat.check_defeat(player) or fitness < -10 or l_neat.completed:
                print("Fitness:", round(fitness, 1))
                genome.fitness += fitness  # Maybe decrease fitness if staggering?
                break

            output = net.activate(l_neat.nparray_to_list(player))  # Maybe try bigger fov
            decision = output.index(max(output))

            if decision == 0:
                pass
            elif decision == 1:
                player.move_up()
            elif decision == 2:
                player.move_right()
            elif decision == 3:
                player.move_left()
            elif decision == 4:
                player.move_right_up()
            elif decision == 5:
                player.move_left_up()

            pygame.display.update()
            self.clock.tick(60)
            self.frame += 1

        return False

    def train_ai_multiple(self, genomes, config):
        players = []
        nets = []
        ge = []
        queues = []

        for g_id, g in genomes:
            g.fitness = 0
            ge.append(g)
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            players.append(Player((0, 0), neat=True))
            queue = deque(maxlen=200)
            queues.append(queue)

        l_neat = Level(level_0, self.screen, players, None, neat=True, multiple_players=True)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return True

            self.screen.fill('grey')
            l_neat.run()

            for index, (player, genome, queue, net) in enumerate(zip(players, ge, queues, nets)):
                dist = l_neat.distance_traveled(player)
                fitness = self.fitness(
                    self.frame, dist, player.coins, l_neat.completed,
                    player.enemies_killed, l_neat.check_defeat(player)
                )

                queue.append(dist)
                if len(queue) == 200:
                    deq = queue
                else:
                    deq = deque([1, 100])
                if deq[-1] - deq[0] < 11 or l_neat.check_defeat(player) or fitness < -10 or l_neat.completed:
                    print("Fitness:", round(fitness, 1))
                    print(dist)
                    genome.fitness += fitness  # Maybe decrease fitness if staggering?
                    players.pop(index)
                    ge.pop(index)
                    queues.pop(index)
                    nets.pop(index)
                    l_neat.remove_player(player)
                    break

                output = net.activate(l_neat.nparray_to_list(player))  # Maybe try bigger fov
                decision = output.index(max(output))

                if decision == 0:
                    pass
                elif decision == 1:
                    player.move_up()
                elif decision == 2:
                    player.move_right()
                elif decision == 3:
                    player.move_left()
                elif decision == 4:
                    player.move_right_up()
                elif decision == 5:
                    player.move_left_up()

            pygame.display.update()
            self.clock.tick(60)
            self.frame += 1

            if len(players) == 0:
                break

        return False


def eval_genomes_multiple(genomes, config):
    game = Platformer()
    force_quit = game.train_ai_multiple(genomes, config)
    if force_quit:
        quit()


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 0
        game = Platformer()
        force_quit = game.train_ai(genome, config)
        if force_quit:
            quit()


def run_neat(config):
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-25')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 50)
    # winner = p.run(eval_genomes_multiple, 500)

    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


def test_neat(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)

    game = Platformer()
    game.test_ai(winner, config)


if __name__ == '__main__':
    # config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         #neat.DefaultSpeciesSet, neat.DefaultStagnation, "config.txt")
    # run_neat(config)
    # test_neat(config)
    game = Platformer()
    game.run()
