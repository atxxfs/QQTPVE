import json
import pygame

from game.frame.frame import Frame

MAGIC_FRAME_ROOT = "game/frame/magic/"
MAGIC_IMG_ROOT = "res/img/magic/"
magics = {}


def get_magic(name):
    if name not in magics.keys():
        magics[name] = load_magic(name)
    return magics[name]


def load_magic(name):
    a_magic = {}
    with open(MAGIC_FRAME_ROOT + '/' + name + ".json") as f:
        magic_json = json.load(f)
    a_magic["STAND"] = list()
    size = len(magic_json["IMG"])
    for i in range(size):
        # print(MAGIC_IMG_ROOT + '/' + magic_json["IMG"][i])
        img = pygame.image.load(MAGIC_IMG_ROOT + '/' + magic_json["IMG"][i]).convert_alpha()
        cx = magic_json["CX"][i]
        cy = magic_json["CY"][i]
        a_magic["STAND"].append(Frame(img, cx, cy))
    return a_magic
