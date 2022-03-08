import pygame
from game.ui.ui import UIInstance


class StatusBar(UIInstance):
    ITEM_IMG_PATH = "res/img/ui/game/"
    ITEM_NUM_PATH = "res/img/ui/number/"

    def __init__(self):
        super().__init__("game", "statusBar")
        self.rect.y = 540
        self.me = None
        self.item_num = None
        self.init_item_num()
        self.set_bubble(0)
        self.set_thunder(0)
        self.set_shoe(0)
        self.prop_imgs_pos = (
            (164, -8), (217, -8), (270, -8), (323, -8), (376, -8), (429, -8), (484, -8)
        )
        self.prop_img_mask_pos = (
            (179, 5), (232, 5), (285, 5), (338, 5), (391, 5), (444, 5), (497, 5)
        )
        self.prop_remain_pos = (
            ((198, 42), (208, 42)),
            ((251, 42), (261, 42)),
            ((304, 42), (314, 42)),
            ((357, 42), (367, 42)),
            ((410, 42), (420, 42)),
            ((463, 42), (473, 42)),
            ((516, 42), (526, 42))
        )
        self.prop_imgs = list()
        self.prop_img_mask = pygame.image.load(StatusBar.ITEM_IMG_PATH + '/' + "img_itemMask.png")
        self.prop_img_mask_on = [True, True, True, True, True, True, True]
        self.prop_remain = [-1, -1, -1, -1, -1, -1, -1]

    def init_item_num(self):
        self.item_num = list()
        for i in range(10):
            file_name = "itemNum_0_" + str(i) + ".png"
            img = pygame.image.load(StatusBar.ITEM_NUM_PATH + '/' + file_name)
            self.item_num.append(img)

    def set_bubble(self, num):
        img = self.item_num[num]
        self.image.blit(img, (48, 42))

    def set_thunder(self, num):
        img = self.item_num[num]
        self.image.blit(img, (100, 42))

    def set_shoe(self, num):
        img = self.item_num[num]
        self.image.blit(img, (152, 42))

    def set_prop_imgs(self, hero):
        self.me = hero
        for i in range(len(hero.skill_names)):
            img = pygame.image.load(StatusBar.ITEM_IMG_PATH + '/' + hero.skill_names[i] + ".png")
            self.prop_imgs.append(img)
        self.redraw()

    def set_prop_remain(self, idx, remain: int):
        remain = max(min(remain, 99), -1)  # 介于-1到99之间
        if self.prop_remain[idx] == remain:
            # 如果数量没变则不重画
            return
        self.prop_remain[idx] = remain
        self.redraw()

    def set_prop_img_mask_on(self, idx, on: bool):
        if self.prop_img_mask_on[idx] == on:
            # 如果蒙版状态没变则不重画
            return
        self.prop_img_mask_on[idx] = on
        self.redraw()

    def update(self):
        # 每一帧都要刷新蒙版和数字
        current_time = pygame.time.get_ticks()
        for i in range(len(self.me.skill_names)):
            # 刷新蒙版
            on = current_time < self.me.skill_init_times[i] or self.me.skill_remains[i] == 0
            self.set_prop_img_mask_on(i, on)
            self.set_prop_remain(i, self.me.skill_remains[i])

    def redraw(self):
        # 更新sheet
        self.redraw_trigger = True
        self.sheet = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
        for i in range(len(self.prop_imgs)):
            # 重画图片
            img = self.prop_imgs[i]
            pos = self.prop_imgs_pos[i]
            self.sheet.blit(img, pos)
            # 重画数字
            num = self.prop_remain[i]
            d2 = num % 10
            if num > -1:
                # 绘制个位
                self.sheet.blit(self.item_num[d2], self.prop_remain_pos[i][1])
            if num > 9:
                # 绘制十位
                d1 = num // 10
                self.sheet.blit(self.item_num[d1], self.prop_remain_pos[i][0])
            # 重画蒙版
            if self.prop_img_mask_on[i]:
                self.sheet.blit(self.prop_img_mask, self.prop_img_mask_pos[i])

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

