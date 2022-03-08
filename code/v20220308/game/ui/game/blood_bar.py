import math
import pygame.font

from game.sprite.player import Player
from game.ui.ui import UIInstance


class BloodBar(UIInstance):

    UI_IMG_GAME_ROOT = "res/img/ui/game/"
    
    def __init__(self, me: Player):
        super(BloodBar, self).__init__("game", "mask_player")
        self.rect.x = 0
        self.rect.y = 120
        self.me = me
        self.current_blood = 0
        self.max_blood = 1
        self.blood_font = pygame.font.Font("res/font/century.ttf", 11)
        self.blood_font.set_bold(True)
        self.blood_slice_img = pygame.image.load(BloodBar.UI_IMG_GAME_ROOT + '/' + "img_playerLife.png")
        self.blood_slice_idx = 90  # 0~90 决定血条的长度
        self.blood_slice_last_update_time = pygame.time.get_ticks()
        self.medal_img = pygame.image.load(BloodBar.UI_IMG_GAME_ROOT + '/' + "medal_30.png")
        self.name = ""
        self.name_font = pygame.font.Font("res/font/simsun.ttc", 12)
        self.init()

    def init(self):
        self.set_max_blood(self.me.blood)

    def update(self):
        self.redraw_trigger = True
        current_time = pygame.time.get_ticks()
        if current_time - self.blood_slice_last_update_time > 100:  # 每100ms刷新一次动画
            self.blood_slice_last_update_time = current_time
            self.sheet = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
            self.set_medal()
            self.set_name(self.name)
            self.current_blood = self.me.remain_blood
            self.set_blood(self.current_blood)
            # 动画改变血条长度
            idx = math.ceil(self.current_blood * 90 / self.max_blood)
            if idx == self.blood_slice_idx:
                return
            if idx < self.blood_slice_idx:
                self.blood_slice_idx -= 1
            elif idx > self.blood_slice_idx:
                self.blood_slice_idx += 1

    def set_max_blood(self, max_blood):
        self.max_blood = min(max(0, max_blood), 9999)
        self.current_blood = self.max_blood
        self.set_blood(self.current_blood)

    def set_blood(self, blood: int):
        blood = min(max(0, blood), self.max_blood)
        text_img = self.blood_font.render(str(blood), False, (0, 255, 255))
        self.sheet.blit(text_img, (2, 2))
        for i in range(self.blood_slice_idx):
            self.sheet.blit(self.blood_slice_img, (i, 16))

    def set_medal(self):
        self.sheet.blit(self.medal_img, (0, 22))

    def set_name(self, name: str):
        self.name = name
        text_img = self.name_font.render(name, False, (255, 255, 255))
        self.sheet.blit(text_img, (26, 24))
