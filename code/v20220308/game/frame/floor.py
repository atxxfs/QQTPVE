import pygame


FLOOR_IMG_ROOT = "res/img/mapElem/"
floors = {}


def get_floor(type, name):
    if type not in floors.keys():
        floors[type] = dict()
    if name not in floors[type].keys():
        # print(FLOOR_IMG_ROOT + type + '/' + name + ".png")
        img = pygame.image.load(FLOOR_IMG_ROOT + type + '/' + name + ".png")
        floors[type][name] = img
    return floors[type][name]
