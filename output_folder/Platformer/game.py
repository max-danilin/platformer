import pygame
import sys
from settings import *
from overworld import Overworld
from player import Player
from ui import UI
from level import Level
from collections import deque
import neat
import logging

# TODO Maybe try data analysis based on ai behaviour
# Logging
log_no_draw = logging.getLogger("platformer")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(module)s - %(levelname)s - %(message)s'))
log_no_draw.addHandler(stream_handler)
log_no_draw.setLevel(logging.INFO)  # DEBUG
stream_handler.setLevel(logging.INFO)  # INFO


class Platformer:
    """
    Main class for the game with main loop

    Use Python 3.7
    """

    def __init__(self, draw=True):
        """
        Initializing pygame, creating player and overworld
        """
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.frame = 0
        self.return_to_initial = False
        self.draw = draw
        pygame.mixer.init()

        self.player = Player((0, 0))
        self.overworld = Overworld(self.screen, self.player)

        pygame.mixer.Channel(BACKGROUND_MUSIC_CHANNEL).set_volume(0.05)

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont(FONT_STD, FONT_SIZE)

    def process_events(self):
        """
        Process occurring events and return them. Process quit and returning to initial screen
        :return:
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                self.return_to_initial = True
            else:
                self.return_to_initial = False
        return events

    def run(self):
        """
        Main game function
        :return:
        """
        while True:
            events = self.process_events()

            self.screen.fill('grey')
            self.overworld.run(events)
            if self.return_to_initial and self.overworld.proceed_to_level is None and self.overworld.return_timeout():
                break

            pygame.display.update()
            self.clock.tick(CLOCK_RATE)

    # NEAT functions
    ####################################
    @staticmethod
    def fitness(frames, distance, score, win, enemy_kills, defeat):
        """
        Fitness function for NEAT implementation
        :param frames: the less frames passed, the better algorithm performs
        :param distance: more distance - better, main parameter to evaluate performance. Also add extra points for
        passing 20 tiles
        :param score: the bigger the score - the better
        :param win: if algorithm reached finish - increase its fitness
        :param enemy_kills: additional points for enemies destroyed (debatable)
        :param defeat: if neat player instance was defeated early in the game - we need to decrease its fitness
        to make evolution less likely to go thi route again
        :return: fitness value
        """
        frames = (frames // CLOCK_RATE)
        distance = int(distance // tile_size)
        if distance < 0:
            distance = 0
        return distance ** 2 - frames ** 1.5 + score ** 1.5 + enemy_kills * 20 + min(max(distance - 20, 0), 1) * 2000 \
               + win * 10000 - defeat * 50

    @staticmethod
    def show_text(font, surface, generation, genome=None, fitness=None, dist=None):
        """
        Displays NEAT info on the screen
        :param dist: distance, travelled by player(only single player NEAT)
        :param genome: genome id(only single player NEAT)
        :param generation: generation number
        :param fitness: fitness at the current moment(only single player NEAT)
        :param font: type of font
        :param surface: surface of our game
        :return:
        """
        surf_gener = font.render(f"Generation: {generation}", True, 'red')
        surface.blit(surf_gener, (300, NEAT_INFO_Y))
        if genome is not None:
            surf_genome = font.render(f"Genome: {genome}", True, 'red')
            surface.blit(surf_genome, (500, NEAT_INFO_Y))
        if fitness is not None:
            surf_fit = font.render(f"Fitness: {fitness}", True, 'red')
            surface.blit(surf_fit, (700, NEAT_INFO_Y))
        if dist is not None:
            surf_fit = font.render(f"Distance: {dist}", True, 'red')
            surface.blit(surf_fit, (900, NEAT_INFO_Y))

    @staticmethod
    def make_decision(decision, player):
        """
        Makes decision what action should player take based on nn response
        :param decision: output from feeding neural network with input
        :param player: player to make decision
        :return:
        """
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

    def get_neat_parameters(self, l_neat, player, queue):
        """
        Getting parameters for current genome of neat
        :param l_neat: level with neat
        :param player: player with neat
        :param queue: queue for player's distance. If its full - use as it is, if not - wait for it to fill and
        use temporary one to match our conditions
        :return: fitness value, distance travelled, queue
        """
        dist = l_neat.distance_traveled(player)
        fitness = self.fitness(
            self.frame, dist, player.coins, l_neat.completed,
            player.enemies_killed, l_neat.check_defeat(player)
        )

        queue.append(dist)
        deq = queue if len(queue) == PLAYER_INACTIVE_LIMIT else deque([1, 100])
        return fitness, dist, deq

    def test_ai(self, genome, config):
        """
        Testing certain trained genome. For more details check train_ai function
        """
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        player = Player((0, 0), neat=True)
        ui = UI(self.screen, player)
        l_neat = Level(level_0, self.screen, player, ui, neat=True)

        while True:
            self.process_events()

            self.screen.fill('grey')
            l_neat.run()
            if l_neat.completed:
                print("Success!")
                self.return_to_initial = True

            output = net.activate(l_neat.nparray_to_list(player))
            decision = output.index(max(output))
            self.make_decision(decision, player)

            pygame.display.update()
            self.clock.tick(CLOCK_RATE)

    def train_ai(self, genome, config, genome_id, generation):
        """
        Function for training genomes of created network. Here's the whole process:
        1. Create player, ui, level and network.
        2. Introduce queue to store player's covered distance in order to check whether player has been moving for
        a duration of PLAYER_INACTIVE_LIMIT. If difference between first and last elements in the queue is less than
        double player's speed then we decide that player is staggering and remove it
        3. We measure travelled distance, fitness, append queue and display text inside main game loop
        4. We remove player in few different scenarios:
            1) it's staggering(based on queue contents)
            2) player was defeated
            3) level was completed
            4) fitness reached minimum FITNESS_LIMIT(have to implement it in cases of player moving in circles)
        5. Feed input from player's fov to neural network, get decision and decide on an output based on it's value.
        Output might be one of the 6 possible player's moves.
        :param generation: generation number
        :param draw: whether to draw level
        :param genome: genome to control player
        :param config: config player
        :param genome_id: id of input genome
        """
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        player = Player((0, 0), neat=True)
        if self.draw:
            ui = UI(self.screen, player)
        else:
            ui = None
        l_neat = Level(level_0, self.screen, player, ui, neat=True, draw=self.draw)
        queue = deque(maxlen=PLAYER_INACTIVE_LIMIT)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    pygame.mixer.stop()
                    self.return_to_initial = True
                    return True

            if self.draw:
                self.screen.fill('grey')
            l_neat.run()
            fitness, dist, deq = self.get_neat_parameters(l_neat, player, queue)
            if deq[-1] - deq[0] < player.speed.x * 2 + 1 or l_neat.check_defeat(player) \
                    or fitness < FITNESS_LIMIT or l_neat.completed:
                genome.fitness += fitness
                if not self.draw:
                    log_no_draw.info(f'Generation: {generation}, genome_id: {genome_id}, fitness: {round(fitness, 1)}, '
                                     f'distance: {int(dist)}')
                break

            output = net.activate(l_neat.nparray_to_list(player))
            decision = output.index(max(output))
            self.make_decision(decision, player)

            if self.draw:
                self.show_text(self.font, self.screen, generation, genome_id, round(fitness, 1), int(dist))
                pygame.display.update()
            self.clock.tick(CLOCK_RATE)
            self.frame += 1

        return False

    def train_ai_multiple(self, genomes, config, generation):
        """
        Function for training NEAT with multiple players simultaneously. For more details check train_ai function.
        The only difference is that we need to work with lists of players, genomes, neural networks and queues.
        Also we use different level function to process multiple players at once. And we dont show UI or other
        text parameters for a single player.
        :param generation: generation number
        :param draw: whether to draw level
        :param genomes: list of genomes to control players
        :param config: config file
        """
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
            queue = deque(maxlen=PLAYER_INACTIVE_LIMIT)
            queues.append(queue)

        l_neat = Level(level_0, self.screen, players, None, neat=True, multiple_players=True, draw=self.draw)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    self.return_to_initial = True
                    pygame.mixer.stop()
                    return True

            if self.draw:
                self.screen.fill('grey')
            l_neat.run()

            for index, (player, genome, queue, net) in enumerate(zip(players, ge, queues, nets)):
                fitness, dist, deq = self.get_neat_parameters(l_neat, player, queue)
                if deq[-1] - deq[0] < player.speed.x * 2 + 1 or l_neat.check_defeat(player) or \
                        fitness < FITNESS_LIMIT or l_neat.completed:
                    log_no_draw.info(f"Fitness: {round(fitness, 1)}")
                    genome.fitness += fitness
                    players.pop(index)
                    ge.pop(index)
                    queues.pop(index)
                    nets.pop(index)
                    l_neat.remove_player(player)
                    break

                output = net.activate(l_neat.nparray_to_list(player))
                decision = output.index(max(output))
                self.make_decision(decision, player)

            if self.draw:
                self.show_text(self.font, self.screen, generation)
                pygame.display.update()
            self.clock.tick(CLOCK_RATE)
            self.frame += 1

            if len(players) == 0:
                break

        return False


if __name__ == '__main__':
    game = Platformer(draw=True)
    game.run()
