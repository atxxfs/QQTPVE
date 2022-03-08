import pygame
from game.ui.ui import UIInstance


class GameTop(UIInstance):

    def __init__(self):
        super().__init__("game", "gameTop")

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        font = pygame.font.Font("res/font/simsun.ttc", 16)
        rend = font.render("v220308", True, (0, 196, 255))
        screen.blit(rend, (0, 0))
