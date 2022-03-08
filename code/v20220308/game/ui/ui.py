import json
import pygame
from enum import Enum


UI_IMG_ROOT = "res/img/ui/"
ui_imgs = {}


def get_ui(type, name):

    if type not in ui_imgs.keys():
        ui_imgs[type] = dict()
    if name not in ui_imgs[type].keys():
        img = pygame.image.load(UI_IMG_ROOT + '/' + type + '/' + name + ".png")
        ui_imgs[type][name] = img
    return ui_imgs[type][name]


class UIInstance(pygame.sprite.Sprite):

    def __init__(self, type, name):
        self.sheet = None  # 与image等大的透明层
        self.redraw_trigger = True  # 当前帧是否需要draw当前sheet 避免重复draw造成负担
        self.load(type, name)

    def load(self, type, name):
        self.image = get_ui(type, name)
        self.rect = self.image.get_rect()
        self.sheet = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)

    def update(self):
        pass

    def draw(self, screen: pygame.Surface):
        if self.redraw_trigger:
            screen.blit(self.image, self.rect)
            screen.blit(self.sheet, self.rect)
            self.redraw_trigger = False


class UIType(Enum):
    BG = 0,
    BTN = 1


class BtnState(Enum):
    PRESSED = 0,
    FORBIDDEN = 1,
    HOVER = 2,
    NORMAL = 3
