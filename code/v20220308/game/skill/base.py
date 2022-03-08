import pygame

from game.const import game as G
from game.effect.effect_instance import EffectState, EffectInstance
from game.level import level
from game.sound import sound_player


class BaseSkill:

    def __init__(self, user, duration, skill_instances):
        self.user = user
        self.duration = duration
        self.skill_instances = skill_instances
        self.init_time = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()
        self.effect_instances = list()
        self.load()

    def load(self):
        # 自身加入玩家skill列表
        self.skill_instances.append(self)

    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time - self.init_time > self.duration:
            self.kill()

    def kill(self):
        # 将所有effect_instance死亡
        for an_effect in self.effect_instances:
            an_effect.state = EffectState.DEAD
        # 自身移除玩家skill列表
        if self in self.skill_instances:
            self.skill_instances.remove(self)


class Launch1(BaseSkill):

    # 第1种蓄力（火泡泡），定身duration秒
    def __init__(self, user, duration, skill_instances):
        super().__init__(user, duration, skill_instances)

    def load(self):
        super().load()
        self.user.rooted_for(self.duration)
        self.effect_instances.append(
            EffectInstance("launch", self.user, True, self.user.effects_behind)
        )


class FireHint(BaseSkill):

    # 火焰提示 指定时长与范围 不跟随使用者
    def __init__(self, user, duration, expand, skill_instances):
        self.expand = expand
        super().__init__(user, duration, skill_instances)

    def load(self):
        super().load()
        for x in range(-self.expand, self.expand + 1):
            for y in range(-self.expand, self.expand + 1):
                an_eff = EffectInstance("fire_hint", self.user, False, level.current_level.effects_behind)
                an_eff.set_xy(self.user.x + x, self.user.y + y)
                self.effect_instances.append(an_eff)


class FireDownAndExplode(BaseSkill):

    # 火焰下落与爆炸
    def __init__(self, user, expand, damage_point, damage_blood, skill_instances):
        self.expand = expand
        self.square_range = range(-self.expand, self.expand + 1)
        self.damage_point = damage_point
        self.damage_blood = damage_blood
        self.effect_fire_down = list()  # 火焰下落动画的effect_instances列表\
        self.state = 0  # 当前状态 0火焰下落 1火焰爆炸
        super().__init__(user, 2000, skill_instances)

    def load(self):
        super().load()
        for x in self.square_range:
            for y in self.square_range:
                an_effect = EffectInstance("fire_down", self.user, False, level.current_level.effects_front)
                an_effect.set_xy(self.damage_point[0] + x, (level.current_level.scroll_y_pos // G.GAME_SQUARE) + y - 3)
                self.effect_instances.append(an_effect)
                self.effect_fire_down.append(an_effect)
        self.at_fire_down()

    def update(self):
        super().update()
        if self.state == 1:
            # 火焰爆炸过程
            for e in self.effect_fire_down:
                e.state = EffectState.DEAD
            for x in self.square_range:
                for y in self.square_range:
                    an_effect = EffectInstance("fire_explode", self.user, False, level.current_level.effects_front)
                    an_effect.set_xy(self.damage_point[0] + x, self.damage_point[1] + y)
                    self.effect_instances.append(an_effect)
                    self.state = 2
        elif self.state == 0:
            # 火焰下落过程
            for e in self.effect_fire_down:
                e.set_xy_pos(e.x_pos, e.y_pos + 35)
                if e.y >= self.damage_point[1]:
                    self.state = 1
                    self.at_fire_explode()

    def at_fire_down(self):
        pass

    def at_fire_explode(self):
        pass


class FireDownAndExplode3x3(FireDownAndExplode):

    def __init__(self, user, damage_point, damage_blood, skill_instances):
        self.hit = False
        super().__init__(user, 1, damage_point, damage_blood, skill_instances)

    def at_fire_down(self):
        if abs(self.user.x - self.damage_point[0]) < 2 and abs(self.user.y - self.damage_point[1]) < 2:
            self.hit = True

    def at_fire_explode(self):
        if self.hit:
            self.user.try_damage(self.damage_blood)


class FireDownAndExplode5x5(FireDownAndExplode):

    def __init__(self, user, damage_point, damage_blood, skill_instances):
        super().__init__(user, 2, damage_point, damage_blood, skill_instances)

    def at_fire_down(self):
        sound_player.play("fire_attack")
        if abs(self.user.x - self.damage_point[0]) < 3 and abs(self.user.y - self.damage_point[1]) < 3:
            self.user.try_damage(self.damage_blood)
            sound_player.play("cry")