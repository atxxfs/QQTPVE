import enum

import pygame

from game.const import game as G
from game.level import level
from game.sprite.updatable import Updatable


class ObstacleInstance(Updatable):

    def __init__(self, x, y, obstacle_instances_dict: dict, obstacle):
        super(ObstacleInstance, self).__init__(x, y)

        self.obstacle = obstacle
        self.state = ObstacleState.NORMAL
        self.obstacle_can_hide = False
        self.obstacle_trigger = False
        self.obstacle_instances_dict: dict = obstacle_instances_dict
        self.has_drawn = False  # 当前帧已经draw过了，避免长宽大于1的障碍在1帧中多次draw，在update中复原
        self.has_updated = False  # 当前帧已经update过了，避免长宽大于1的障碍在1帧中多次update，在draw中复原
        self.setup()

        self.obstacle_timer = 0  # obstacle帧计时器
        self.obstacle_frame_idx = 0  # obstacle帧索引
        self.cx = self.cy = 0  # obstacle显示的偏移

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.update()

    def setup(self):

        # 添加obstacle_instances字典映射
        for x in range(self.obstacle["WIDTH"]):
            for y in range(self.obstacle["HEIGHT"]):
                self.obstacle_instances_dict[(x + self.x), (y + self.y)] = self

        # 添加block三维数组
        for orient in range(2):
            for x in range(len(self.obstacle["BLOCK"][orient])):
                for y in range(len(self.obstacle["BLOCK"][orient][x])):
                    level.current_level.block[orient][x + self.x][y + self.y] += self.obstacle["BLOCK"][orient][x][y]

        if self.obstacle["CAN_HIDE"]:
            self.obstacle_can_hide = True

        if "TRIGGER" in self.obstacle:
            self.obstacle_trigger = True

    def within_screen(self):
        # 【非常重要！！】障碍显示优化 只显示屏幕区域内的障碍物！
        # 以下几行代码极大地提升了性能，使理论最低帧数由90降至50
        a = self.x_pos < level.current_level.scroll_x_pos + G.MAIN_AREA_X_POS + G.HALF_GAME_SQUARE
        b = self.y_pos < level.current_level.scroll_y_pos + G.MAIN_AREA_Y_POS + G.HALF_GAME_SQUARE
        c = self.x_pos + self.obstacle["WIDTH"] * G.GAME_SQUARE > level.current_level.scroll_x_pos
        d = self.y_pos + self.obstacle["HEIGHT"] * G.GAME_SQUARE > level.current_level.scroll_y_pos
        if a and b and c and d:
            return True
        else:
            return False

    def trigger(self):
        # 激活障碍
        if "TRIGGER" not in self.obstacle:
            return
        if self.state == ObstacleState.DEAD or self.state == ObstacleState.DYING:
            return
        if not self.within_screen():
            return
        self.switch_state(ObstacleState.TRIGGERING)

    def update(self):
        if self.state == ObstacleState.DEAD:
            return
        if self.within_screen() and not self.has_updated:
            current_time = pygame.time.get_ticks()
            self.update_frame(current_time)
            self.has_updated = True
            self.has_drawn = False

    def update_frame(self, current_time):
        if current_time - self.obstacle_timer > self.obstacle["INTERVAL"]:
            category = self.get_category()
            LEN = len(self.obstacle[category])
            if LEN == 0:
                self.frame_loop()
                return
            if self.obstacle_frame_idx + 1 == LEN:
                self.frame_loop()
            self.obstacle_frame_idx = (self.obstacle_frame_idx + 1) % LEN
            self.cx = self.obstacle[category][self.obstacle_frame_idx].cx
            self.cy = self.obstacle[category][self.obstacle_frame_idx].cy
            self.obstacle_timer = current_time
            self.image = self.obstacle[category][self.obstacle_frame_idx].image
            self.rect.x = self.x * G.GAME_SQUARE + self.obstacle[category][self.obstacle_frame_idx].cx
            self.rect.y = self.y * G.GAME_SQUARE + self.obstacle[category][self.obstacle_frame_idx].cy
            # 写入redraw_tuples
            # x_range = range(self.rect.x // G.GAME_SQUARE, (self.rect.x + self.image.get_width()) // G.GAME_SQUARE + 1)
            # y_range = range(self.rect.y // G.GAME_SQUARE, (self.rect.y + self.image.get_height()) // G.GAME_SQUARE + 1)
            # for x in x_range:
            #     for y in y_range:
            #         level.current_level.obstacle_redraw_tuples.add((x, y))

    def get_category(self):
        # 根据obstacle状态枚举 获取帧类型str
        category = "STAND"
        if self.state == ObstacleState.DYING:
            category = "DIE"
        if self.state == ObstacleState.TRIGGERING:
            category = "TRIGGER"
        return category

    def frame_loop(self):
        # 帧循环即将回到第1帧
        if self.state == ObstacleState.DYING:
            self.switch_state(ObstacleState.DEAD)
            self.uninstall()
        if self.state == ObstacleState.TRIGGERING:
            self.switch_state(ObstacleState.NORMAL)

    def switch_state(self, new_state):
        # 切换到指定状态 并重置帧索引
        self.state = new_state
        self.obstacle_frame_idx = -1

    def die(self):
        # 摧毁障碍 尝试进入DYING状态
        if self.state == ObstacleState.DEAD or self.state == ObstacleState.DYING:
            return
        if self.obstacle["BREAKABLE"] is False:
            return
        self.switch_state(ObstacleState.DYING)

    def draw(self, screen: pygame.Surface):
        if self.within_screen() and not self.has_drawn:
            super().draw(screen)
            self.has_updated = False
            self.has_drawn = True

    def uninstall(self):

        # 取消obstacle_instances字典映射
        for x in range(self.obstacle["WIDTH"]):
            for y in range(self.obstacle["HEIGHT"]):
                self.obstacle_instances_dict.pop((x + self.x, y + self.y))

        for orient in range(2):
            for x in range(len(self.obstacle["BLOCK"][orient])):
                for y in range(len(self.obstacle["BLOCK"][orient][x])):
                    level.current_level.block[orient][x + self.x][y + self.y] -= self.obstacle["BLOCK"][orient][x][y]

        level.current_level.recal_npc_paths = True


class ObstacleState(enum.Enum):
    DEAD = -2
    DYING = -1
    NORMAL = 0
    TRIGGERING = 1
