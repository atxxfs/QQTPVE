import json

import numpy as np
import pygame
from game.const import game as G

OBSTACLE_FRAME_ROOT = "game/frame/obstacle/"
OBSTACLE_IMG_ROOT = "res/img/mapElem/"
obstacles = {}


def get_obstacle(type, name):
    if type not in obstacles.keys():
        obstacles[type] = dict()
    if name not in obstacles[type].keys():
        obstacles[type][name] = load_obstacle(type, name)
    return obstacles[type][name]


def get_merged_obstacle(type, name, width, height):
    obs = get_obstacle(type, name)
    dup_obs = load_obstacle(type, name)
    dup_obs["WIDTH"] = width
    dup_obs["HEIGHT"] = height
    dup_obs["BLOCK"] = np.zeros((2, width + 1, height + 1), dtype=np.int)
    dup_obs["STAND"][0].image = pygame.Surface((width * G.GAME_SQUARE + G.GAME_SQUARE, height * G.GAME_SQUARE + G.GAME_SQUARE), pygame.SRCALPHA, 32)
    for x in range(width):
        for y in range(height):
            dup_obs["STAND"][0].image.blit(obs["STAND"][0].image, (G.GAME_SQUARE * x, G.GAME_SQUARE * y))
            dup_obs["BLOCK"][0][x + 0][y + 0] += obs["BLOCK"][0][0][0]
            dup_obs["BLOCK"][0][x + 0][y + 1] += obs["BLOCK"][0][0][1]
            dup_obs["BLOCK"][1][x + 0][y + 0] += obs["BLOCK"][1][0][0]
            dup_obs["BLOCK"][1][x + 1][y + 0] += obs["BLOCK"][1][1][0]
    return dup_obs


def load_obstacle(type, name):

    an_obstacle = {}
    # print(OBSTACLE_FRAME_ROOT + type + '/' + name + ".json")
    with open(OBSTACLE_FRAME_ROOT + type + '/' + name + ".json") as f:
        obstacle_json = json.load(f)
    an_obstacle["WIDTH"] = obstacle_json["WIDTH"]
    an_obstacle["HEIGHT"] = obstacle_json["HEIGHT"]
    an_obstacle["BLOCK"] = obstacle_json["BLOCK"]
    an_obstacle["BREAKABLE"] = obstacle_json["BREAKABLE"]
    an_obstacle["CAN_HIDE"] = obstacle_json["CAN_HIDE"]
    an_obstacle["INTERVAL"] = obstacle_json["INTERVAL"]

    append_obstacle(obstacle_json, an_obstacle, "STAND")
    append_obstacle(obstacle_json, an_obstacle, "DIE")
    append_obstacle(obstacle_json, an_obstacle, "TRIGGER")

    return an_obstacle


def append_obstacle(obstacle_json, an_obstacle, state: str):

    if state in obstacle_json:
        an_obstacle[state] = list()
        frames = obstacle_json[state]
        size = len(frames["IMG"])
        for i in range(size):
            img = pygame.image.load(OBSTACLE_IMG_ROOT + obstacle_json["TYPE"] + '/' + frames["IMG"][i])
            cx = frames["CX"][i]
            cy = frames["CY"][i]
            an_obstacle[state].append(Frame(img, cx, cy))


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy
