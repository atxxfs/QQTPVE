import json
import os
import sys

import pygame

from game.const import window as W, color as C
from game.frame import character, magic
from game.level.level import Level
from game.sprite.hero import Hero


class Game:

    def __init__(self):
        # 游戏配置
        self.cfg_json = None
        self.your_name = None  # 玩家名称
        self.map_set_json = None
        self.map_set_at = -1  # 当前在map_set的第几关 从0开始
        self.npc_name_card = None  # 显示npc姓名牌
        self.music_volume = None  # 游戏音乐音量大小
        self.frame_rate = None  # 游戏帧速率
        self.grid_damage_duration = None  # 网格伤害持续时间
        self.display_flags = pygame.NOFRAME  # 画面显示特征

        # 游戏值
        self.me = None  # 玩家Hero对象
        self.current_level = None  # 当前关卡Level对象
        self.orientations = dict()  # 方向键与字符串的映射
        self.walking_stack = []  # 方向键栈
        self.bomb_old = False  # 连按空格键标志
        self.f6_old = False  # 连按F6键标志
        self.skills_old = [False, False, False, False, False, False, False]  # 连按技能键标志
        self.key2idx = dict()  # 数字键与技能下标的映射
        self.cfg_space = None  # 用户自定义空格
        self.cfg_f6 = None  # 用户自定义f6

        # 初始化pygame
        pygame.init()
        pygame.display.set_caption(W.WINDOW_CAPTION)
        self.init_game()
        self.screen = pygame.display.set_mode(W.WINDOW_SIZE, flags=self.display_flags)
        self.preload()
        self.proceed_game()
        self.update()

    def init_game(self):
        # 游戏初始化 读取配置文件
        with open("config.json", encoding="utf-8") as f:
            self.cfg_json = json.load(f)
        self.npc_name_card = self.cfg_json["npc_name_card"]
        self.music_volume = self.cfg_json["music_volume"]
        self.frame_rate = int(self.cfg_json["frame_rate"])
        self.grid_damage_duration = int(self.cfg_json["grid_damage_duration"])
        self.your_name = self.cfg_json["your_name"]
        self.init_keys(self.cfg_json["keys"])
        if self.cfg_json["full_screen"]:
            self.display_flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        with open("game/map_set/" + self.cfg_json["map_set"] + ".json") as f:
            self.map_set_json = json.load(f)

    def init_keys(self, keys_root):
        # 加载自定义按键
        self.orientations[keys_root["RIGHT"]] = "R"
        self.orientations[keys_root["UP"]] = "U"
        self.orientations[keys_root["LEFT"]] = "L"
        self.orientations[keys_root["DOWN"]] = "D"
        self.key2idx[keys_root["1"]] = 0
        self.key2idx[keys_root["2"]] = 1
        self.key2idx[keys_root["3"]] = 2
        self.key2idx[keys_root["4"]] = 3
        self.key2idx[keys_root["5"]] = 4
        self.key2idx[keys_root["6"]] = 5
        self.key2idx[keys_root["7"]] = 6
        self.cfg_space = keys_root["SPACE"]
        self.cfg_f6 = keys_root["F6"]

    def preload(self):
        if not self.cfg_json["allow_preload"]:
            return
        ch_root = "game/frame/character/"
        for f in os.listdir(ch_root):
            with open(ch_root + f) as tf:
                jf = json.load(tf)
                character.get_character(jf, C.CHARACTER_RED)
        mg_root = "game/frame/magic/"
        for f in os.listdir(mg_root):
            name = f.split('.')[0]
            magic.get_magic(name)

    def proceed_game(self):
        # 进入下一个关卡
        self.map_set_at += 1
        map_name = self.map_set_json["maps"][self.map_set_at]
        hero_name = self.cfg_json["your_hero"]
        character_color = self.cfg_json["your_character_color"]
        self.set_level(self.your_name, map_name, hero_name, character_color)

    def set_level(self, your_name, map_name, hero_name, character_color):
        # 改变当前关卡
        if character_color == "Red":
            character_color = C.CHARACTER_RED
        elif character_color == "Blue":
            character_color = C.CHARACTER_BLUE
        # 保留我的技能剩余数
        me = Hero(hero_name, (0, 0), character_color)
        if self.me is not None:
            me.skill_remains = self.me.skill_remains
        self.me = me
        # 保留显示npc姓名牌状态
        if self.current_level is None:
            display_name_card = self.npc_name_card
        else:
            display_name_card = self.current_level.display_name_card
        # 设置新关卡
        self.current_level = Level(your_name, map_name, self.me, self.music_volume, self.grid_damage_duration)
        self.current_level.display_name_card = display_name_card

    def update(self):
        # 事件处理
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

            # 键盘事件
            self.key_pressed()

            # 更新关卡
            if self.current_level is not None:
                if self.current_level.finish_flag:
                    # 如果过关
                    self.proceed_game()
                else:
                    # 正常刷新
                    self.current_level.update(self.screen)

            # 刷新显示
            pygame.display.update()

            # 设置帧率
            pygame.time.Clock().tick(self.frame_rate)

    def key_pressed(self):
        # 键盘事件检测
        keys = pygame.key.get_pressed()
        self.player_move(keys)
        self.player_bomb(keys)
        self.player_f6(keys)
        self.player_skill(keys)

    def player_move(self, keys):
        # 玩家移动
        # 取放按键栈
        for enum in self.orientations.keys():
            if keys[enum]:
                if enum not in self.walking_stack:
                    self.walking_stack.insert(0, enum)
            else:
                if enum in self.walking_stack:
                    self.walking_stack.remove(enum)
        # 取栈顶元素first
        first = 0
        if len(self.walking_stack) > 0:
            first = self.walking_stack[0]
        # 判断first是哪个方向
        if first == 0:
            self.me.set_motion()
        else:
            self.me.set_motion(self.orientations[first])

    def player_bomb(self, keys):
        if keys[self.cfg_space]:
            if self.bomb_old is True:
                return
            # 按下空格键
            self.me.set_bomb()
            self.bomb_old = True
        else:
            self.bomb_old = False

    def player_f6(self, keys):
        if keys[self.cfg_f6]:
            if self.f6_old is True:
                return
            # 按下F6键
            self.current_level.switch_name_card()
            self.f6_old = True
        else:
            self.f6_old = False

    def player_skill(self, keys):
        for k in self.key2idx.keys():
            idx = self.key2idx[k]  # 常量转索引
            if keys[k]:
                if self.skills_old[idx]:
                    return
                self.me.use_skill(idx)
                self.skills_old[idx] = True
            else:
                self.skills_old[idx] = False
