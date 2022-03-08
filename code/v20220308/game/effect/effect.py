import json
import pygame

from game.frame import magic
from game.frame.frame import Frame

EFFECT_ROOT = "game/effect/effect/"
effects = {}


def get_effect(name):

    if name not in effects.keys():
        effects[name] = load_effect(name)
    return effects[name]


def load_effect(name):

    an_effect = {}
    with open(EFFECT_ROOT + '/' + name + ".json") as f:
        effect_json = json.load(f)
    magic_len = len(effect_json["MAGICS"])
    an_effect["magics"] = list()
    for i in range(magic_len):
        magic_root = effect_json["MAGICS"][i]
        magic_name = magic_root["NAME"]
        a_magic = magic.load_magic(magic_name)
        a_magic_instance = dict()
        a_magic_instance["cx"] = magic_root["CX"]
        a_magic_instance["cy"] = magic_root["CY"]
        a_magic_instance["repeat"] = magic_root["REPEAT"]
        a_magic_instance["interval"] = magic_root["INTERVAL"]
        a_magic_instance["special_flag"] = magic_root["SPECIAL_FLAG"]
        if "MAX_TIME" in magic_root.keys():
            a_magic_instance["max_time"] = magic_root["MAX_TIME"]
        a_magic_instance["frames"] = list()
        for j in range(len(a_magic["STAND"])):
            f: Frame = a_magic["STAND"][j].duplicate()
            size = f.image.get_rect().size
            mask = pygame.Surface(size)
            if "ALPHA" in magic_root.keys():
                f.image.set_alpha(magic_root["ALPHA"][j])
            if "COLOR_ADD" in magic_root.keys():
                mask.fill(magic_root["COLOR_ADD"])
                f.image.blit(mask, (0, 0), special_flags=pygame.BLEND_ADD)
            if "COLOR_SUB" in magic_root.keys():
                mask.fill(magic_root["COLOR_SUB"])
                f.image.blit(mask, (0, 0), special_flags=pygame.BLEND_SUB)
            a_magic_instance["frames"].append(f)
        an_effect["magics"].append(a_magic_instance)

    return an_effect
