import json
import pygame

ITEM_FRAME_ROOT = "game/frame/item/"
ITEM_IMG_ROOT = "res/img/item/"
items = {}


def get_item(name):
    if name not in items.keys():
        items[name] = load_item(name)
    return items[name]


def load_item(name):
    an_item = {}
    with open(ITEM_FRAME_ROOT + '/' + name + ".json") as f:
        item_json = json.load(f)
    an_item["INTERVAL"] = item_json["INTERVAL"]
    an_item["STAND"] = list()
    size = len(item_json["STAND"]["IMG"])
    for i in range(size):
        # print(ITEM_IMG_ROOT + '/' + item_json["STAND"]["IMG"][i])
        img = pygame.image.load(ITEM_IMG_ROOT + '/' + item_json["STAND"]["IMG"][i])
        cx = item_json["STAND"]["CX"][i]
        cy = item_json["STAND"]["CY"][i]
        an_item["STAND"].append(Frame(img, cx, cy))
    return an_item


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy
