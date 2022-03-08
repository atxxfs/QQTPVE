import json
import pygame

BOMB_FRAME_ROOT = "game/frame/bomb/"
BOMB_IMG_ROOT = "res/img/bomb/"
bombs = {}


def get_bomb(name):
    if name not in bombs.keys():
        bombs[name] = load_bomb(name)
    return bombs[name]


def load_bomb(name):
    a_bomb = {}
    with open(BOMB_FRAME_ROOT + name + ".json") as f:
        bomb_json = json.load(f)
    a_bomb["INTERVAL"] = bomb_json["INTERVAL"]
    a_bomb["STAND"] = list()
    size = len(bomb_json["STAND"]["IMG"])
    for i in range(size):
        img = pygame.image.load(BOMB_IMG_ROOT + '/' + bomb_json["STAND"]["IMG"][i])
        cx = bomb_json["STAND"]["CX"][i]
        cy = bomb_json["STAND"]["CY"][i]
        a_bomb["STAND"].append(Frame(img, cx, cy))
    return a_bomb


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy
