import enum
import pygame

from game.const import game as G
from game.frame import flame
from game.level import level
from game.sprite.updatable import Updatable


class FlameInstance(Updatable):

    def __init__(self, x, y, flame, seq):

        super(FlameInstance, self).__init__(x, y)

        self.flame = flame  # 已经确定了方向的flame
        self.seq = None  # 动画帧序列枚举
        self.get_seq(seq)  # 获取帧序列

        self.state = FlameState.NORMAL
        self.flame_timer = 0  # flame计时器
        self.flame_frame_idx = 0  # flame帧索引
        self.cx = self.cy = 0  # flame显示的偏移

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.update()

    def get_seq(self, seq):

        self.seq = flame.flame_seq[int(seq)]

    def update(self):

        if self.state == FlameState.DEAD:
            return
        current_time = pygame.time.get_ticks()
        self.update_frame(current_time)
        self.if_hide()

    def update_frame(self, current_time):

        if current_time - self.flame_timer > 40:
            self.blank_img()
            LEN = len(self.seq)
            if self.flame_frame_idx == LEN:
                self.switch_state(FlameState.DEAD)
                return
            self.cx = self.flame[self.seq[self.flame_frame_idx]].cx
            self.cy = self.flame[self.seq[self.flame_frame_idx]].cy
            self.image = self.flame[self.seq[self.flame_frame_idx]].image
            self.rect.x = self.x_pos - G.HALF_GAME_SQUARE + self.flame[self.seq[self.flame_frame_idx]].cx
            self.rect.y = self.y_pos - G.HALF_GAME_SQUARE + self.flame[self.seq[self.flame_frame_idx]].cy
            self.flame_timer = current_time
            self.flame_frame_idx += 1

    def switch_state(self, new_state):
        # 切换到指定状态 并重置帧索引
        self.state = new_state
        self.flame_frame_idx = 0


class FlameState(enum.Enum):
    NORMAL = 0
    DEAD = -1


class FlameType(enum.IntEnum):
    END_INSTANT = 1
    END_DELAYED = 2
    MID_INSTANT = 3
    MID_DELAYED = 4
    MID_THROUGH = 5
