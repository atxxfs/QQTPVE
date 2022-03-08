import json

import pygame

from game.const import color as C
from game.const import game as G
from game.frame import bomb
from game.level import level
from game.skill.skill import Protect3s, Indicator, BloodElixirMiddle, BloodElixirSmall, BloodElixirLarge, PowerElixir, \
    MockingElixir, HeroSword, FriendlyElixir, HeiLongFloatingFire, HeroFloatingFire, RevivalCard
from game.sound import sound_player
from game.sprite.bomb_instance import BombInstance
from game.sprite.player import Player, PlayerState


class Hero(Player):

    def __init__(self, hero_name, xy, color=C.CHARACTER_RED):

        super(Hero, self).__init__(hero_name, xy, color)
        self.hero_json = None
        self.bomb_skin = None  # Hero糖泡皮肤（get_bomb的返回值）
        self.icon_img = None  # Hero左侧图片
        self.bomb = 0  # Hero糖泡数
        self.power = 0  # Hero糖泡威力
        self.restore = 0  # Hero糖泡回复速度（ms/个）
        self.damage = 0  # Hero糖泡单倍伤害
        self.remain_bombs = 0  # 当前Hero剩余可放糖泡数
        self.bomb_time_old = pygame.time.get_ticks()  # 上次放置糖泡的时刻

        self.rooted = 1
        self.rooted_begin = pygame.time.get_ticks()
        self.rooted_duration = 3000

        self.load_hero(hero_name, color)
        Protect3s(self, self.skill_instances)
        Indicator(self, self.skill_instances)

    def load_hero(self, hero_name, color):
        # 加载人物hero的json文件
        with open("game/hero/" + hero_name + ".json") as f:
            self.hero_json = json.load(f)
            self.bomb_skin = bomb.get_bomb(self.hero_json["bomb_skin"])
            self.icon_img = self.hero_json["icon_img"]
            self.blood = self.hero_json["blood"]
            self.speed = (self.hero_json["speed"] * G.GAME_SQUARE) / 1000
            self.bomb = self.hero_json["bomb"]
            self.power = self.hero_json["power"]
            self.restore = self.hero_json["restore"]
            self.damage = self.hero_json["damage"]
            self.defense = self.hero_json["defense"]
            for s in self.hero_json["skills"]:
                self.skill_names.append(s["name"])
                self.skill_init_times.append(s["init"] + pygame.time.get_ticks())
                self.skill_intervals.append(s["interval"])
                self.skill_remains.append(s["max"])
            self.remain_blood = self.blood
            self.remain_bombs = self.bomb
            self.character = self.load_character(self.hero_json["character"], color)

    def set_bomb(self):
        # 尝试放置一个糖泡
        if self.state != PlayerState.NORMAL:
            return
        if self.remain_bombs <= 0:
            return
        p = (self.x, self.y)
        bis = level.current_level.bomb_instances
        bs = level.current_level.get_bomb_instance(*p)
        if len(bs) > 0:  # 当前位置有糖泡
            return
        sound_player.play("bomb")
        BombInstance(*p, bis, self.bomb_skin, self.power, self.damage, self)
        self.remain_bombs -= 1
        self.bomb_time_old = pygame.time.get_ticks()

    def update(self):
        super().update()
        current_time = pygame.time.get_ticks()
        self.time_restore_a_bomb(current_time)
        self.check_district_lock()

    def stimulate_x_y_changed_trigger(self):
        super().stimulate_x_y_changed_trigger()
        if self.x_y_changed_trigger:
            level.current_level.recal_npc_paths = True

    def time_restore_a_bomb(self, current_time):
        if current_time - self.bomb_time_old > self.restore:
            self.bomb_time_old = current_time
            self.restore_a_bomb()

    def restore_a_bomb(self):
        if self.remain_bombs >= self.bomb:
            return
        self.remain_bombs += 1

    def check_district_lock(self):
        if self.district_locked:
            return
        square = level.current_level.district_square
        if square is None:
            return
        if square["x1"] <= self.x_pos <= square["x2"] and square["y1"] <= self.y_pos <= square["y2"]:
            self.district_locked = True
            self.collide_district()

    def collide_district(self):
        # Hero碰撞区域 红色提示
        level.current_level.alarm_district()

    def die(self):
        sound_player.play("hero_dead")
        for n in level.current_level.npcs:
            n.resentful = False

    def use_skill(self, idx: int):
        if idx > len(self.skill_names) - 1:
            # 技能越界返回
            return
        if self.state == PlayerState.LOSE and self.skill_names[idx] != "RevivalCard":
            # 人物死亡返回
            return
        cl = level.current_level
        current_time = pygame.time.get_ticks()
        if current_time < self.skill_init_times[idx] or self.skill_remains[idx] == 0:
            # 未到初始时间 或技能冷却中 或次数已用完（-1则可以无限使用）
            return
        name = self.skill_names[idx]
        if name == "BloodElixirSmall":
            BloodElixirSmall(self, self.skill_instances)
        elif name == "BloodElixirMiddle":
            BloodElixirMiddle(self, self.skill_instances)
        elif name == "BloodElixirLarge":
            BloodElixirLarge(self, self.skill_instances)
        elif name == "PowerElixir":
            PowerElixir(self, self.skill_instances)
        elif name == "FriendlyElixir":
            FriendlyElixir(self, level.current_level.npcs, self.skill_instances)
        elif name == "MockingElixir":
            MockingElixir(self, level.current_level.npcs, self.skill_instances)
        elif name == "RevivalCard":
            RevivalCard(self, self.skill_instances)
        elif name == "HeroSword":
            HeroSword(self, level.current_level.npcs, self.skill_instances)
        elif name == "HeroFloatingFire":
            HeroFloatingFire(self, level.current_level.npcs, self.skill_instances)
        self.skill_remains[idx] -= 1  # 剩余数量-1
        self.skill_init_times[idx] = current_time + self.skill_intervals[idx]  # 冷却时间累加
