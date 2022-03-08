import pygame

pygame.mixer.init()
PATH = "res/sound"


def play(name):
    pygame.mixer.Sound(PATH + '/' + name + ".wav").play()
