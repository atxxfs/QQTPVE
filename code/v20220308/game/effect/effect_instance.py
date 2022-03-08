import enum
import pygame

from game.const import game as G
from game.effect import effect
from game.frame import magic
from game.level import level
from game.sound import sound_player


class EffectInstance:

    def __init__(self, effect_name: str, user, follow: bool, effect_instances):

        super().__init__()
        self.user = user
        self.follow = follow
        self.effect_instances = effect_instances
        self.x = user.x
        self.y = user.y
        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE

        self.state = EffectState.NORMAL
        self.effect_time_init = pygame.time.get_ticks()  # effect初始时间
        self.effect_time_max = 0  # effect最大时间
        self.effect_frame_timer = list()  # 每个effect帧计时器（在0~interval之间循环）
        self.effect_frame_idx = list()  # 每个effect帧索引
        self.effect = effect.get_effect(effect_name)
        for i in range(len(self.effect["magics"])):
            self.effect_frame_idx.append(0)  # 为每一个effect图层创建一个idx索引
            self.effect_frame_timer.append(self.effect_time_init)  # 为每一个magic_instance创建一个计时器
        self.effect_instances.append(self)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        self.x_pos = x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
        self.y_pos = y * G.GAME_SQUARE + G.HALF_GAME_SQUARE

    def set_xy_pos(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x = x_pos // G.GAME_SQUARE
        self.y = y_pos // G.GAME_SQUARE

    def update(self):

        if self.state == EffectState.DEAD:
            self.effect_instances.remove(self)
            return
        if self.follow:
            self.x = self.user.x
            self.y = self.user.y
            self.x_pos = self.user.x_pos
            self.y_pos = self.user.y_pos
        current_time = pygame.time.get_ticks()
        self.update_frame(current_time)

    def update_frame(self, current_time):

        for i in range(len(self.effect["magics"])):
            a_magic_instance = self.effect["magics"][i]
            repeat = a_magic_instance["repeat"]
            interval = a_magic_instance["interval"]
            frames = a_magic_instance["frames"]
            if current_time - self.effect_frame_timer[i] > interval:
                self.effect_frame_timer[i] = current_time
                self.effect_frame_idx[i] += 1
                if self.effect_frame_idx[i] >= len(frames):  # 如果magic_instance播放完了
                    if not repeat:
                        continue  # 不重复 则不再播放
                    self.effect_frame_idx[i] = 0  # 重复 则从头播放

    def draw(self, screen: pygame.Surface):

        if self.state == EffectState.DEAD:
            return
        for i in range(len(self.effect["magics"])):
            a_magic_instance = self.effect["magics"][i]
            if "max_time" in a_magic_instance.keys():
                if pygame.time.get_ticks() - self.effect_time_init > a_magic_instance["max_time"]:
                    continue  # 对于超时的magic直接跳过
            frames = a_magic_instance["frames"]
            if self.effect_frame_idx[i] >= len(frames):
                continue  # 对于播放完的magic，直接跳过
            img = frames[self.effect_frame_idx[i]].image
            cx = self.x_pos + frames[self.effect_frame_idx[i]].cx + a_magic_instance["cx"]
            cy = self.y_pos + frames[self.effect_frame_idx[i]].cy + a_magic_instance["cy"]
            screen.blit(img, (cx, cy), special_flags=a_magic_instance["special_flag"])
            #  BLENDMODE_NONE = 0
            #  BLEND_ADD = 1
            #  BLEND_SUB = 2
            #  BLEND_MIN = 4
            #  BLEND_MAX = 5
            #  BLEND_PREMULTIPLIED = 17


class EffectState(enum.Enum):

    NORMAL = 0
    DEAD = -1


class ReadyGo:

    def __init__(self, effect_instances):
        self.effect_instances = effect_instances
        self.state = EffectState.NORMAL
        self.ready = pygame.image.load(magic.MAGIC_IMG_ROOT + '/' + "magic0135_0_0.png")
        self.go = pygame.image.load(magic.MAGIC_IMG_ROOT + '/' + "magic0136_0_0.png")
        self.line = pygame.image.load(magic.MAGIC_IMG_ROOT + '/' + "magic0137_0_0.png")
        self.frame_idx = -1
        self.ready_x_pos = (-600, -554, -508, -462, -416, -370, -324, -278, -232, -186, -140, -94, -48, -2, 44, 50, 40, 30, 20, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.ready_cx = 120
        self.ready_cy = 200
        self.ready_alpha = (255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 251, 247, 243, 239, 235, 231, 227, 223, 219, 215, 211, 207, 203, 199, 195, 191, 187, 183, 179, 175, 171, 167, 163, 159, 155, 151, 147, 143, 139, 135, 131, 127, 123, 119, 115, 111, 107, 103, 99, 95, 91, 87, 83, 79, 75, 71, 67, 63, 59, 55, 51, 47, 43, 39, 35, 31, 27, 23, 19, 15, 0)
        self.go_x_pos = (-600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -600, -554, -508, -462, -416, -370, -324, -278, -232, -186, -140, -94, -48, -2, 44, 50, 40, 30, 20, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.go_cx = 200
        self.go_cy = 200
        self.go_alpha = (255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 230, 205, 180, 155, 130, 105, 80, 55, 30, 0)
        self.line_x_pos = (-600, -560, -520, -480, -440, -400, -360, -320, -280, -240, -200, -160, -120, -80, -40, 0, 24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384, 408, 432, 456, 480, 504, 528, 552, 576, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, -600, -560, -520, -480, -440, -400, -360, -320, -280, -240, -200, -160, -120, -80, -40, 0, 24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384, 408, 432, 456, 480, 504, 528, 552, 576, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600)
        self.line_cx = 160
        self.line_cy = 200
        self.line_alpha = (255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 245, 235, 225, 215, 205, 195, 185, 175, 165, 155, 145, 135, 125, 115, 105, 95, 85, 75, 65, 55, 45, 35, 25, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 245, 235, 225, 215, 205, 195, 185, 175, 165, 155, 145, 135, 125, 115, 105, 95, 85, 75, 65, 55, 45, 35, 25, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        sound_player.play("ready_go")
        self.effect_instances.append(self)

    def update(self):
        if self.state == EffectState.DEAD:
            self.effect_instances.remove(self)
            return
        self.frame_idx += 1
        if self.frame_idx >= 100:
            self.state = EffectState.DEAD
            return

    def draw(self, screen: pygame.Surface):
        self.ready.set_alpha(self.ready_alpha[self.frame_idx])
        screen.blit(self.ready, (self.ready_x_pos[self.frame_idx] + self.ready_cx, self.ready_cy))
        self.go.set_alpha(self.go_alpha[self.frame_idx])
        screen.blit(self.go, (self.go_x_pos[self.frame_idx] + self.go_cx, self.go_cy))
        self.line.set_alpha(self.line_alpha[self.frame_idx])
        screen.blit(self.line, (self.line_x_pos[self.frame_idx] + self.line_cx, self.line_cy), special_flags=1)


class DistrictAlarm:

    def __init__(self, effect_instances):
        self.effect_instances = effect_instances
        self.img_alpha = (64, 128, 192, 255, 192, 128, 64)

        self.frame_idx = -1
        self.frame_timer = pygame.time.get_ticks()
        self.district_alarm_img = pygame.image.load("res/img/magic/magic0193_0_0.png")
        self.district_alarm_imgs: pygame.Surface = None

        self.load()

    def load(self):

        cl = level.current_level
        cl.district_alarming = True
        x1 = cl.district_square["x1"]
        x2 = cl.district_square["x2"]
        y1 = cl.district_square["y1"]
        y2 = cl.district_square["y2"]
        x_range = range(int((x2 - x1) / G.GAME_SQUARE) + 1)
        y_range = range(int((y2 - y1) / G.GAME_SQUARE) + 1)
        self.district_alarm_imgs = pygame.Surface((x2 - x1 + G.GAME_SQUARE, y2 - y1 + G.GAME_SQUARE), pygame.SRCALPHA, 32)

        for x in x_range:
            for y in y_range:
                self.district_alarm_imgs.blit(self.district_alarm_img, (x * G.GAME_SQUARE, y * G.GAME_SQUARE))

        self.effect_instances.append(self)

    def update(self):

        current_time = pygame.time.get_ticks()
        if current_time - self.frame_timer > 50:
            self.frame_idx += 1
            self.frame_timer = current_time
        if self.frame_idx >= 7:
            level.current_level.district_alarming = False
            self.effect_instances.remove(self)

    def draw(self, screen: pygame.Surface):
        cl = level.current_level
        self.district_alarm_imgs.set_alpha(self.img_alpha[self.frame_idx])
        screen.blit(
            self.district_alarm_imgs,
            (cl.district_square["x1"] - G.HALF_GAME_SQUARE, cl.district_square["y1"] - G.HALF_GAME_SQUARE)
        )


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y
