import json
import pygame

FLAME_JSON_ROOT = "game/frame/flame/"
FLAME_JSON_FILE = "flame.json"
FLAME_IMG_ROOT = "res/img/flame/"
ORIENTATIONS = ("FLAME_C", "FLAME_R", "FLAME_U", "FLAME_L", "FLAME_D")
flames = {}
flame_seq = None

with open(FLAME_JSON_ROOT + '/' + FLAME_JSON_FILE) as f:
    j = json.load(f)
    flame_seq = j["FLAME_SEQ"]


def get_flame(orientation):

    if orientation not in flames.keys():
        flames[orientation] = list()
        with open(FLAME_JSON_ROOT + '/' + FLAME_JSON_FILE) as f:
            flame_json = json.load(f)
        root = flame_json[orientation]
        size = len(root["IMG"])
        for i in range(size):
            img = pygame.image.load(FLAME_IMG_ROOT + '/' + root["IMG"][i])
            cx = root["CX"][i]
            cy = root["CY"][i]
            a_flame = Frame(img, cx, cy)
            flames[orientation].append(a_flame)

    return flames[orientation]


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy
