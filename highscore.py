import pygame
import hashlib
from settings import HASH_KEY, HIGHSCORES_DIR


class HighScore:
    """
    Class for displaying high scores
    """
    def __init__(self, surface):
        self.surface = surface
        self.highscores = []

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 40)

    def draw(self):
        """
        Displays loaded high scores
        :return:
        """
        self.surface.fill("black")

        x = 50
        y = 130
        # Initial text
        self.font.bold = True
        surf_high = self.font.render("High scores:", True, "red")
        self.surface.blit(surf_high, (50, 50))
        surf_name = self.font.render("Name", True, "red")
        self.surface.blit(surf_name, (x, y))
        surf_score = self.font.render("Coins", True, "red")
        self.surface.blit(surf_score, (x + 200, y))
        surf_kills = self.font.render("Enemies destroyed", True, "red")
        self.surface.blit(surf_kills, (x + 400, y))

        # High scores
        y = 200
        self.font.bold = False
        for item in self.highscores:
            surf_name = self.font.render(item[0], True, "red")
            self.surface.blit(surf_name, (x, y))
            surf_score = self.font.render(str(item[1]), True, "red")
            self.surface.blit(surf_score, (x+200, y))
            surf_kills = self.font.render(str(item[2]), True, "red")
            self.surface.blit(surf_kills, (x+400, y))
            y += 40

    @staticmethod
    def add(name, score, kills):
        """
        Adds name,score and kills to highscore.dat using blake2b hash function and utf-8 encoding
        :param name: typed in name
        :param score: number of coins
        :param kills: number of enemies destroyed
        :return:
        """
        hash = hashlib.blake2b()
        hash.update(str(name + str(score) + HASH_KEY).encode('utf-8'))

        with open(HIGHSCORES_DIR, "a") as f:
            f.write(name + "[::]" + str(score) + "[::]" + str(kills) + "[::]" + str(hash.hexdigest() + "\n"))

    def load(self):
        """
        Load highscores from file and sort in descending order, display only first 10 records
        :return:
        """
        with open(HIGHSCORES_DIR, 'r') as f:
            for line in f:
                name, score, kills, hash = line.strip("\n").split("[::]")
                hashed = hashlib.blake2b(str.encode(name + str(score) + HASH_KEY)).hexdigest()
                if hashed == hash:
                    self.highscores.append([name, int(score), int(kills)])
        self.highscores.sort(key=lambda x: x[1], reverse=True)
        self.highscores = self.highscores[0:11]
