import enum
import pygame

from game.const import game as G
from game.level import level
from game.sprite.throwable import Throwable
from game.sprite.player import Player


class ItemInstance(Throwable):

    def __init__(self, x, y, item_instances_dict: dict, item):

        super(ItemInstance, self).__init__(x, y)

        self.item_instances_dict: dict = item_instances_dict
        self.item = item

        self.state = ItemState.NORMAL

        self.item_timer = 0  # item帧计时器
        self.item_frame_idx = 0  # item帧索引0
        self.cx = self.cy = 0  # item显示的偏移

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.update()

    def update(self):

        if self.state == ItemState.DEAD:
            return
        current_time = pygame.time.get_ticks()
        if self.state == ItemState.NORMAL:
            self.throw()
            self.update_frame(current_time)
            self.if_hide()

    def update_frame(self, current_time):

        if current_time - self.item_timer > self.item["INTERVAL"]:
            LEN = len(self.item["STAND"])
            self.item_frame_idx = (self.item_frame_idx + 1) % LEN
            self.cx = self.item["STAND"][self.item_frame_idx].cx
            self.cy = self.item["STAND"][self.item_frame_idx].cy
            self.item_timer = current_time
            self.image = self.item["STAND"][self.item_frame_idx].image
        self.rect.x = self.x_pos - G.HALF_GAME_SQUARE + self.item["STAND"][self.item_frame_idx].cx
        self.rect.y = self.y_pos - G.HALF_GAME_SQUARE + self.item["STAND"][self.item_frame_idx].cy

    def switch_state(self, new_state):
        # 切换到指定状态 并重置帧索引
        self.state = new_state
        self.item_frame_idx = 0

    def if_hide(self):
        # 判断item_instance是否隐藏
        if (self.x, self.y) in level.current_level.obstacle_instances:
            self.blank_img()

    def player_get(self, p: Player):
        # 某一player获得该item
        pass

    def set_restoration(self, to_x, to_y):
        self.x = to_x
        self.y = to_y
        self.item_instances_dict.pop((self.x, self.y))
        self.item_instances_dict[(to_x, to_y)] = self


class ItemState(enum.Enum):
    DEAD = -1
    NORMAL = 0

