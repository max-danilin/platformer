import pygame
import hashlib


class HighScore:  # TODO Refactor
    def __init__(self, surface):
        self.surface = surface
        self.highscores = []

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 40)

    def draw(self):
        self.surface.fill("black")

        surf_high = self.font.render("High scores:", True, "red")
        self.surface.blit(surf_high, (50, 50))
        x = 50
        y = 130
        self.font.bold = True
        surf_name = self.font.render("Name", True, "red")
        self.surface.blit(surf_name, (x, y))
        surf_score = self.font.render("Coins", True, "red")
        self.surface.blit(surf_score, (x + 200, y))
        surf_kills = self.font.render("Enemies destroyed", True, "red")
        self.surface.blit(surf_kills, (x + 400, y))
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

    def add(self, name, score, kills):
        hash = hashlib.blake2b()
        hash.update(str(name + str(score) + "maxd").encode('utf-8'))

        with open("highscore.dat", "a") as f:
            f.write(name + "[::]" + str(score) + "[::]" + str(kills) + "[::]" + str(hash.hexdigest() + "\n"))

    def load(self):
        with open("highscore.dat", 'r') as f:
            for line in f:
                name, score, kills, hash = line.strip("\n").split("[::]")
                hashed = hashlib.blake2b(str.encode(name + str(score) + "maxd")).hexdigest()
                if hashed == hash:
                    self.highscores.append([name, int(score), int(kills)])
        self.highscores.sort(key=lambda x: x[1], reverse=True)
        self.highscores = self.highscores[0:11]
