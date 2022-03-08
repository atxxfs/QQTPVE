import json
import random

import pygame

from game.const import color as C
from game.const import game as G
from game.level import level
from game.skill.base import FireDownAndExplode, FireDownAndExplode3x3, Launch1, FireHint
from game.skill.skill import ThunderAttack, HeiLongBlackWizardPutFireTrap, \
    HeiLongBlackWizardPutIceTrap, HeiLongAbyssDragonSword, HeiLongAbyssDragonDistantFire, HeiLongAbyssDragonCharge, \
    HeiLongCubDragonBluePutFireTrap, HeiLongDistantFire5x5, HeiLongDistantFire3x3, HeiLongDizzy9x9, \
    HeiLongThunder3x3HP800, HeiLongPutThunderTrap, HeiLongRedWizardPutFireTrap, HeiLongReverse, BloodElixirMiddle, \
    HeiLongFloatingFire, HeiLongHellDragonDistantFire, HeiLongHellDragonCharge, HeiLongHellDragonScope
from game.sound import sound_player
from game.sprite.hero import Hero
from game.sprite.player import Player, PlayerState


class Npc(Player):

    def __init__(self, npc_name, xy, color=C.CHARACTER_RED):

        super(Npc, self).__init__(npc_name, xy, color)
        self.npc_json = None
        self.chs_name = None  # Npc中文名
        self.idx_motion = {0: "R", 1: "U", 2: "L", 3: "D"}
        self.contact = 0  # Npc接触伤害
        self.resent_dist = None  # Npc仇恨范围（几格以内）
        self.resentful = False  # Npc玩家仇恨
        self.mocking = False  # Npc受到嘲笑药水的作用暂时仇恨
        self.friendly = False  # Npc受到玫瑰药水的作用暂时解除仇恨
        self.wander_random = 10  # Npc在无仇恨时的闲逛时间
        self.district_locked = True
        self.chase_path = None  # Npc追踪路径
        self.npc_skill_time = pygame.time.get_ticks()  # npc施放技能时的时刻 设为成员变量是为了统一多个技能的时间
        self.chs_name_bg = pygame.image.load("res/img/ui/game/misc171.png")  # Npc姓名牌背景
        self.chs_name_font = pygame.font.Font("res/font/simsun.ttc", 13)  # Npc姓名牌字体
        self.chs_name_text = None  # Npc姓名牌前景文字
        self.chs_name_text_shadow = None  # Npc姓名牌背景文字
        self.chs_name_text_half_width = None  # Npc姓名牌文字的半宽 用于居中显示文字

        self.load_npc(npc_name, color)

    def load_npc(self, npc_name, color):
        # 加载npc的json文件
        with open("game/npc/" + npc_name + ".json", encoding="utf-8") as f:
            self.npc_json = json.load(f)
            self.chs_name = self.npc_json["chs_name"]
            self.blood = self.npc_json["blood"]
            self.speed = (self.npc_json["speed"] * G.GAME_SQUARE) / 1000
            self.contact = self.npc_json["contact"]
            self.defense = self.npc_json["defense"]
            self.resent_dist = self.npc_json["resent_dist"] * G.GAME_SQUARE  # 仇恨距离（像素）
            for s in self.npc_json["skills"]:
                self.skill_names.append(s["name"])
                self.skill_init_times.append(s["init"])
                self.skill_intervals.append(s["interval"])
                self.skill_remains.append(s["max"])
            self.remain_blood = self.blood
            self.chase_path = dict()
            self.chs_name_text = self.chs_name_font.render(self.chs_name, True, (255, 255, 0))
            self.chs_name_text_shadow = self.chs_name_font.render(self.chs_name, True, (0, 0, 0))
            self.chs_name_text_half_width = self.chs_name_text.get_width() // 2
            self.character = self.load_character(self.npc_json["character"], color)

    def update(self):
        super().update()
        current_time = pygame.time.get_ticks()
        self.wander_and_detect(current_time)
        self.try_using_skills()

    def wander_and_detect(self, current_time):
        # 游走并检测玩家距离
        if (self.resentful or self.mocking) and not self.friendly:
            return
        # 随机运动时间
        if current_time % 15 == 0:
            motion = self.idx_motion[random.randint(0, 3)]
            self.set_motion(motion)
        # 技能初始时间更新
        for i in range(len(self.skill_names)):
            # 游荡状态下，技能初始时间永远等于当前时刻加init值
            self.skill_init_times[i] = self.npc_json["skills"][i]["init"] + current_time
        # 检测与玩家的距离
        me: Hero = level.current_level.me
        if me.district_locked and me.state == PlayerState.NORMAL:
            if abs(me.x_pos - self.x_pos) < self.resent_dist and abs(me.y_pos - self.y_pos) < self.resent_dist:
                # 如果玩家活着、已进入区域锁，并且距离小于临界值 则产生玩家仇恨
                self.resentful = True
                level.current_level.recal_npc_paths = True

    def die(self):
        sound_player.play("npc_dead")

    def collide_wall(self):
        # npc 游走时撞墙 则改变方向
        if self.orientation == "U":
            self.set_motion("D")
        if self.orientation == "D":
            self.set_motion("U")
        if self.orientation == "L":
            self.set_motion("R")
        if self.orientation == "R":
            self.set_motion("L")

    def try_using_skills(self):
        # npc 循环使用技能
        if not self.resentful and not self.mocking or self.friendly:
            return
        # npc 技能时间更新
        self.npc_skill_time = pygame.time.get_ticks()
        # 每一帧都尝试使用全部技能
        for i in range(len(self.skill_names)):
            self.use_skill(i)

    def use_skill(self, idx: int):
        cl = level.current_level
        if self.npc_skill_time < self.skill_init_times[idx] or self.skill_remains[idx] == 0:
            # 未到初始时间 或技能冷却中 或次数已用完（-1则可以无限使用）
            return
        name = self.skill_names[idx]
        if name == "ThunderAttack":
            ThunderAttack(self, self.skill_instances)
        elif name == "FireHint":
            FireHint(self, 600, 1, self.skill_instances)
        elif name == "BloodElixirMiddle":
            BloodElixirMiddle(self, self.skill_instances)
        elif name == "FireDownAndExplode3x3":
            FireDownAndExplode3x3(cl.me, (cl.me.x, cl.me.y), 500, cl.skill_instances)
        elif name == "HeiLongReverse":
            HeiLongReverse(self, [cl.me], self.skill_instances)
        elif name == "HeiLongBlackWizardPutIceTrap":
            HeiLongBlackWizardPutIceTrap(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongBlackWizardPutFireTrap":
            HeiLongBlackWizardPutFireTrap(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongAbyssDragonDistantFire":
            HeiLongAbyssDragonDistantFire(self, [cl.me], self.skill_instances)
        elif name == "HeiLongAbyssDragonCharge":
            HeiLongAbyssDragonCharge(self, self.skill_instances)
        elif name == "HeiLongAbyssDragonSword":
            HeiLongAbyssDragonSword(self, [cl.me], self.skill_instances)
        elif name == "HeiLongCubDragonBluePutFireTrap":
            HeiLongCubDragonBluePutFireTrap(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongDistantFire5x5":
            HeiLongDistantFire5x5(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongDistantFire3x3":
            HeiLongDistantFire3x3(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongDizzy9x9":
            HeiLongDizzy9x9(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongThunder3x3HP800":
            HeiLongThunder3x3HP800(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongPutThunderTrap":
            HeiLongPutThunderTrap(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongRedWizardPutFireTrap":
            HeiLongRedWizardPutFireTrap(self, [cl.me], cl.skill_instances)
        elif name == "HeiLongFloatingFire":
            HeiLongFloatingFire(self, [cl.me], self.skill_instances)
        elif name == "HeiLongHellDragonDistantFire":
            HeiLongHellDragonDistantFire(self, [cl.me], self.skill_instances)
        elif name == "HeiLongHellDragonCharge":
            HeiLongHellDragonCharge(self, self.skill_instances)
        elif name == "HeiLongHellDragonScope":
            HeiLongHellDragonScope(self, [cl.me], self.skill_instances)
        self.skill_remains[idx] -= 1
        self.skill_init_times[idx] += self.skill_intervals[idx]

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        if level.current_level.display_name_card:
            screen.blit(self.chs_name_bg, (self.x_pos - 40, self.y_pos - 100))
            screen.blit(self.chs_name_text_shadow, (self.x_pos + 3 - self.chs_name_text_half_width, self.y_pos - 95))
            screen.blit(self.chs_name_text, (self.x_pos + 2 - self.chs_name_text_half_width, self.y_pos - 95))
