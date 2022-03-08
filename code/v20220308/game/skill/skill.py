from math import sqrt

import pygame

from game.const import game as G
from game.effect.effect_instance import EffectState, EffectInstance
from game.level import level
from game.sound import sound_player


class Skill:

    def __init__(self, user, to: list, skill_instances):
        self.user = user
        self.to = to
        self.user_x = self.user.x  # 记录Player施法时的xy格子 全程不变
        self.user_y = self.user.y
        self.skill_instances = skill_instances
        self.skill_time_init = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()
        self.effect_instances = list()
        self.load()

    def load(self):
        # 自身加入玩家skill列表
        self.skill_instances.append(self)

    def update(self):
        self.current_time = pygame.time.get_ticks()

    def kill(self):
        # 将所有effect_instance死亡
        for an_effect in self.effect_instances:
            an_effect.state = EffectState.DEAD
        # 自身移除玩家skill列表
        if self in self.skill_instances:
            self.skill_instances.remove(self)


class Protect3s(Skill):

    def __init__(self, user, skill_instances):
        super(Protect3s, self).__init__(user, None, skill_instances)

    def load(self):
        super().load()
        self.user.protected += 1
        self.effect_instances.append(
            EffectInstance("protect", self.user, True, self.user.effects_front)
        )

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init >= 3000:
            self.kill()

    def kill(self):
        super().kill()
        self.user.protected -= 1


class Indicator(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("indicator", self.user, True, self.user.effects_front)
        )


class ThunderAttack(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)
        self.flag_thunder_down = True  # 300ms
        self.flag_thunder_explode = True  # 400ms

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("thunder_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("launch")
        self.user.rooted_for(300)
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 900:
            self.kill()
        if self.current_time - self.skill_time_init > 200 and self.flag_thunder_down:
            self.flag_thunder_down = False
            for x in range(self.user_x - 1, self.user_x + 2):
                for y in range(self.user_y - 1, self.user_y + 2):
                    an_effect = EffectInstance("thunder_down", self.user, False, self.user.effects_front)
                    an_effect.x_pos = x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                    an_effect.y_pos = y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                    self.effect_instances.append(an_effect)
        if self.current_time - self.skill_time_init > 500 and self.flag_thunder_explode:
            self.flag_thunder_explode = False
            me = level.current_level.me
            for x in range(self.user_x - 1, self.user_x + 2):
                for y in range(self.user_y - 1, self.user_y + 2):
                    an_effect = EffectInstance("thunder_explode", self.user, False, self.user.effects_front)
                    an_effect.x_pos = x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                    an_effect.y_pos = y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                    self.effect_instances.append(an_effect)
                    if me.x == x and me.y == y:
                        me.try_damage(200)


class BloodElixir(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)
        self.heal_blood = 0
        self.effect_name = ""

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance(self.effect_name, self.user, True, self.user.effects_front)
        )
        sound_player.play("drink")
        self.user.rooted_for(500)
        self.user.align_xy()
        self.user.heal(self.heal_blood)

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 800:
            self.kill()


class BloodElixirSmall(BloodElixir):

    def __init__(self, user, skill_instances):
        self.heal_blood = 500
        self.effect_name = "blood_elixir_small"
        super().__init__(user, skill_instances)


class BloodElixirMiddle(BloodElixir):

    def __init__(self, user, skill_instances):
        self.heal_blood = 1000
        self.effect_name = "blood_elixir_middle"
        super().__init__(user, skill_instances)


class BloodElixirLarge(BloodElixir):

    def __init__(self, user, skill_instances):
        self.heal_blood = 2000
        self.effect_name = "blood_elixir_large"
        super().__init__(user, skill_instances)


class PowerElixir(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)
        self.violent = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("power_elixir", self.user, True, self.user.effects_front)
        )
        sound_player.play("drink")
        self.user.rooted_for(500)
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 30000:
            self.kill()
        if self.current_time - self.skill_time_init > 800 and self.violent:
            self.violent = False
            self.user.damage += 300
            self.effect_instances.append(
                EffectInstance("violent", self.user, True, self.user.effects_front)
            )

    def kill(self):
        super().kill()
        self.user.damage -= 300


class FriendlyElixir(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("friendly_elixir", self.user, True, self.user.effects_front)
        )
        sound_player.play("drink")
        self.user.rooted_for(500)
        self.user.align_xy()
        for to in self.to:
            to.friendly = True

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 10000:
            self.kill()

    def kill(self):
        super().kill()
        for to in self.to:
            to.friendly = False


class MockingElixir(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("mocking_elixir", self.user, True, self.user.effects_front)
        )
        sound_player.play("drink")
        self.user.rooted_for(500)
        self.user.align_xy()
        for to in self.to:
            to.mocking = True

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 10000:
            self.kill()

    def kill(self):
        super().kill()
        for to in self.to:
            to.mocking = False


class RevivalCard(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("revival_card", self.user, True, self.user.effects_front)
        )
        sound_player.play("launch")
        self.user.rooted_for(500)
        self.user.align_xy()
        self.user.revive(500)

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 20000:
            self.kill()


class HeiLongReverse(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.reversing = True
        self.xy_old = dict()  # 施法时记录玩家旧xy值

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 4000:
            self.kill()
        if self.current_time - self.skill_time_init > 1000 and self.reversing:
            self.reversing = False
            self.user.rooted -= 1
            for to in self.to:
                self.effect_instances.append(
                    EffectInstance("reverse", to, True, to.effects_front)
                )
                to.reverse_for(3000)
        if self.loaded:
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            self.effect_instances.append(
                EffectInstance("poison_charge", self.user, True, self.user.effects_front)
            )


class HeiLongBlackWizardPutIceTrap(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.ice_trap = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("ice_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("trap")
        self.user.rooted += 1
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 13000:
            self.kill()
        if self.current_time - self.skill_time_init > 950 and self.ice_trap:
            self.ice_trap = False
            self.effect_instances.append(
                EffectInstance("ice_trap", self.user, False, level.current_level.effects_behind)
            )
            self.user.rooted -= 1
        if self.current_time - self.skill_time_init > 950:
            # 判断玩家是否踩中陷阱
            for to in self.to:
                if to.x == self.user_x and to.y == self.user_y:
                    to.try_damage(500)
                    self.kill()


class HeiLongBlackWizardPutFireTrap(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.fire_trap = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("fire_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("trap")
        self.user.rooted += 1
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 31000:
            self.kill()
        if self.current_time - self.skill_time_init > 950 and self.fire_trap:
            self.fire_trap = False
            self.effect_instances.append(
                EffectInstance("fire_trap", self.user, False, level.current_level.effects_behind)
            )
            self.user.rooted -= 1
        if self.current_time - self.skill_time_init > 950:
            # 判断玩家是否踩中陷阱
            for to in self.to:
                if to.x == self.user_x and to.y == self.user_y:
                    to.try_damage(800)
                    EffectInstance("got_fire", to, True, to.effects_front)
                    self.kill()


class HeiLongAbyssDragonDistantFire(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.distant_fire_attack = True
        self.damage_blood = 250
        self.xy_old = dict()  # 施法时记录玩家旧xy值

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 1500:
            self.kill()
        if self.current_time - self.skill_time_init > 1000 and self.distant_fire_attack:
            self.distant_fire_attack = False
            self.user.rooted -= 1
            for to in self.to:
                an_effect = EffectInstance("got_burned", to, False, to.effects_front)
                an_effect.set_xy(self.xy_old[to][0], self.xy_old[to][1])  # 着火动画要在玩家的旧位置播放
                if to.x == self.xy_old[to][0] and to.y == self.xy_old[to][1]:
                    to.try_damage(self.damage_blood)
        if self.current_time - self.skill_time_init > 0 and self.loaded:
            self.loaded = False
            self.effect_instances.append(
                EffectInstance("fire_charge", self.user, True, self.user.effects_front)
            )
            sound_player.play("trap")
            self.user.rooted += 1
            self.user.align_xy()
            for to in self.to:
                self.xy_old[to] = (to.x, to.y)


class HeiLongAbyssDragonCharge(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)
        self.loaded = True
        self.smoke = True
        self.cancel_recovery = True
        self.effect_recovery = None
        self.effect_firework = None

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 13000:
            self.user.contact -= 300
            self.effect_firework.state = EffectState.DEAD
            self.kill()
        if self.current_time - self.skill_time_init > 7500 and self.cancel_recovery:
            self.cancel_recovery = False
            self.effect_recovery.state = EffectState.DEAD
        if self.current_time - self.skill_time_init > 3000 and self.smoke:
            self.smoke = False
            self.user.rooted -= 1
            self.user.contact += 300
            sound_player.play("launch")
            self.effect_firework = EffectInstance("firework_blue", self.user, True, self.user.effects_front)
            self.effect_instances.append(self.effect_firework)
            self.effect_recovery = EffectInstance("recovery", self.user, True, self.user.effects_front)
            self.effect_instances.append(self.effect_recovery)
            for x in range(-2, 3):
                for y in range(-2, 3):
                    an_effect = EffectInstance("smoke", self.user, False, self.user.effects_front)
                    an_effect.set_xy(self.user.x - x, self.user.y - y)
                    self.effect_instances.append(an_effect)
        if self.current_time - self.skill_time_init > 0 and self.loaded:
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            sound_player.play("launch")


class Sword5x5(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.real_damage = False  # 是否造成真实伤害
        self.damage_blood = 0

    def load(self):
        self.effect_instances.append(
            EffectInstance("sword", self.user, True, self.user.effects_front)
        )
        self.user.align_xy()
        for to in self.to:
            if abs(to.x - self.user.x) < 3 and abs(to.y - self.user.y) < 3:
                if self.real_damage:
                    to.real_damage(self.damage_blood)
                else:
                    to.try_damage(self.damage_blood)
                EffectInstance("thunder_explode", to, True, to.effects_front)

    def update(self):
        if self.current_time - self.skill_time_init > 500:
            self.kill()


class HeroSword(Sword5x5):

    def __init__(self, user, to, skill_instances):
        self.damage_blood = 1000
        self.real_damage = True
        super().__init__(user, to, skill_instances)


class HeiLongAbyssDragonSword(Sword5x5):

    def __init__(self, user, to, skill_instances):
        self.damage_blood = 800
        self.real_damage = False
        super().__init__(user, to, skill_instances)


class HeiLongCubDragonBluePutFireTrap(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.fire_trap = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("fire_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("trap")
        self.user.rooted += 1
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 21000:
            self.kill()
        if self.current_time - self.skill_time_init > 950 and self.fire_trap:
            self.fire_trap = False
            self.effect_instances.append(
                EffectInstance("fire_trap", self.user, False, level.current_level.effects_behind)
            )
            self.user.rooted -= 1
        if self.current_time - self.skill_time_init > 950:
            # 判断玩家是否踩中陷阱
            for to in self.to:
                if to.x == self.user_x and to.y == self.user_y:
                    to.try_damage(20)
                    EffectInstance("got_burned", to, True, to.effects_front)
                    self.kill()


class HeiLongDistantFire5x5(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.hint_end = True  # 结束火焰提示标志
        self.fire_down = True  # 火焰开始下落
        self.fire_down_finish = True  # 火焰开始完成
        self.fire_explode = True  # 火焰触碰到地面
        self.fire_trap = True
        self.to_xy = dict()  # 火焰提示时玩家的xy
        self.effect_fire_down = list()  # 火焰下落动画的effect_instances列表
        self.finish_y = 0  # 底端火焰的最终y值

    def load(self):
        super().load()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 2000:
            self.kill()
        if self.fire_explode and not self.fire_down_finish:
            # 火焰最终爆炸
            self.fire_explode = False
            for e in self.effect_instances:
                e.state = EffectState.DEAD
            for to in self.to:
                for x in range(-2, 3):
                    for y in range(-2, 3):
                        an_effect = EffectInstance("fire_explode", self.user, False, level.current_level.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, self.to_xy[to][1] + y)
                        self.effect_instances.append(an_effect)
        if not self.fire_down and self.fire_down_finish:
            # 火焰下落过程
            for e in self.effect_fire_down:
                e.set_xy_pos(e.x_pos, e.y_pos + 35)
                if e.y >= self.finish_y:
                    self.fire_down_finish = False
        if self.current_time - self.skill_time_init > 800 and self.fire_down:
            # 火焰开始下落
            self.fire_down = False
            sound_player.play("fire_attack")
            for to in self.to:
                # 伤害判断
                if abs(self.to_xy[to][0] - to.x) < 3 and abs(self.to_xy[to][1] - to.y) < 3:
                    to.try_damage(50)
                    EffectInstance("defect", to, True, to.effects_front)
                    sound_player.play("cry")
                for x in range(-2, 3):
                    for y in range(-2, 3):
                        an_effect = EffectInstance("fire_down", self.user, False, level.current_level.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, (level.current_level.scroll_y_pos // G.GAME_SQUARE) + y - 3)
                        self.effect_instances.append(an_effect)
                        self.effect_fire_down.append(an_effect)
        if self.current_time - self.skill_time_init > 500 and self.hint_end:
            # 取消火焰提示与npc施法阵
            self.hint_end = False
            self.user.rooted -= 1
            for e in self.effect_instances:
                e.state = EffectState.DEAD
        if self.loaded:
            # 显示火焰提示与npc施法阵
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            self.effect_instances.append(
                EffectInstance("launch", self.user, False, self.user.effects_behind)
            )
            for to in self.to:
                self.to_xy[to] = (to.x, to.y)
                self.finish_y = to.y
                for x in range(-2, 3):
                    for y in range(-2, 3):
                            an_effect = EffectInstance("fire_hint", self.user, False, level.current_level.effects_behind)
                            an_effect.set_xy(to.x + x, to.y + y)
                            self.effect_instances.append(an_effect)
            sound_player.play("launch")


class HeiLongDistantFire3x3(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.fire_down = True  # 火焰开始下落
        self.fire_down_finish = True  # 火焰开始完成
        self.fire_explode = True  # 火焰触碰到地面
        self.to_xy = dict()  # 火焰提示时玩家的xy
        self.effect_fire_down = list()  # 火焰下落动画的effect_instances列表
        self.finish_y = 0  # 底端火焰的最终y值
        self.hit = False  # 是否命中了玩家

    def load(self):
        super().load()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 1200:
            self.kill()
        if self.fire_explode and not self.fire_down_finish:
            # 火焰最终爆炸
            self.fire_explode = False
            for e in self.effect_instances:
                e.state = EffectState.DEAD
            for to in self.to:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        an_effect = EffectInstance("fire_explode", self.user, False, level.current_level.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, self.to_xy[to][1] + y)
                        self.effect_instances.append(an_effect)
                if self.hit:
                    to.try_damage(500)
        if not self.fire_down and self.fire_down_finish:
            # 火焰下落过程
            for e in self.effect_fire_down:
                e.set_xy_pos(e.x_pos, e.y_pos + 35)
                if e.y >= self.finish_y:
                    self.fire_down_finish = False
        if self.current_time - self.skill_time_init > 200 and self.fire_down:
            # 火焰开始下落
            self.fire_down = False
            self.user.rooted -= 1
            for e in self.effect_instances:
                e.state = EffectState.DEAD
            for to in self.to:
                # 伤害判断
                if abs(self.to_xy[to][0] - to.x) < 2 and abs(self.to_xy[to][1] - to.y) < 2:
                    self.hit = True
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        an_effect = EffectInstance("fire_down", self.user, False, level.current_level.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, (level.current_level.scroll_y_pos // G.GAME_SQUARE) + y - 2)
                        self.effect_instances.append(an_effect)
                        self.effect_fire_down.append(an_effect)
        if self.loaded:
            # npc施法阵
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            self.effect_instances.append(
                EffectInstance("thunder_charge", self.user, False, self.user.effects_front)
            )
            # 记录玩家初始位置与火焰结束位置
            for to in self.to:
                self.to_xy[to] = (to.x, to.y)
                self.finish_y = to.y
            sound_player.play("launch")


class HeiLongDizzy9x9(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.dizzy_explode = True  # 眩晕爆炸

    def load(self):
        super().load()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 5000:
            self.kill()
        if self.current_time - self.skill_time_init > 1000 and self.dizzy_explode:
            # 眩晕爆炸
            self.dizzy_explode = False
            self.user.rooted -= 1
            for to in self.to:
                # 伤害判断
                if abs(self.user_x - to.x) < 2 and abs(self.user_y - to.y) < 2:
                    to.try_damage(500)
                for x in range(-4, 5):
                    for y in range(-4, 5):
                        an_effect = EffectInstance("dizzy_explode", self.user, False, level.current_level.effects_front)
                        an_effect.set_xy(self.user_x + x, self.user_y + y)
                        self.effect_instances.append(an_effect)
        if self.loaded:
            # npc施法阵与眩晕范围提示
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            self.effect_instances.append(
                EffectInstance("launch2", self.user, False, self.user.effects_front)
            )
            # 眩晕范围提示
            for x in range(-4, 5):
                for y in range(-4, 5):
                    an_effect = EffectInstance("dizzy_hint", self.user, False, level.current_level.effects_behind)
                    an_effect.set_xy(self.user_x + x, self.user_y + y)
                    self.effect_instances.append(an_effect)
            sound_player.play("launch")


class HeiLongThunder3x3HP500(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True  # 0ms
        self.thunder_down = True  # 300ms
        self.thunder_explode = True  # 600ms
        self.to_xy = dict()  # 火焰提示时玩家的xy
        self.hit = False  # 是否命中玩家
        self.damage_blood = 500  # 击中后伤血量

    def load(self):
        super().load()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 1000:
            self.kill()
        if self.current_time - self.skill_time_init > 600 and self.thunder_explode:
            self.thunder_explode = False
            for to in self.to:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        an_effect = EffectInstance("thunder_explode", self.user, False, self.user.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, self.to_xy[to][1] + y)
                        self.effect_instances.append(an_effect)
                if self.hit:
                    to.try_damage(self.damage_blood)
                    to.rooted_for(500)
        if self.current_time - self.skill_time_init > 280 and self.thunder_down:
            self.thunder_down = False
            self.user.rooted -= 1
            for e in self.effect_instances:
                e.state = EffectState.DEAD
            for to in self.to:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        an_effect = EffectInstance("thunder_down", self.user, False, self.user.effects_front)
                        an_effect.set_xy(self.to_xy[to][0] + x, self.to_xy[to][1] + y)
                        self.effect_instances.append(an_effect)
                        # 判断是否击中玩家
                        if self.to_xy[to][0] + x == to.x and self.to_xy[to][1] + y == to.y:
                            self.hit = True
        if self.loaded:
            self.loaded = False
            sound_player.play("launch")
            self.user.rooted += 1
            self.user.align_xy()
            for to in self.to:
                self.to_xy[to] = (to.x, to.y)
            self.effect_instances.append(
                EffectInstance("thunder_charge", self.user, False, self.user.effects_front)
            )


class HeiLongThunder3x3HP800(HeiLongThunder3x3HP500):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.damage_blood = 800


class HeiLongPutThunderTrap(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.thunder_trap = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("thunder_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("trap")
        self.user.rooted += 1
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 10000:
            self.kill()
        if not self.thunder_trap:
            # 判断玩家是否踩中陷阱
            for to in self.to:
                if to.x == self.user_x and to.y == self.user_y:
                    to.try_damage(299)
                    to.rooted_for(3000)
                    EffectInstance("thunder_fixed", to, True, level.current_level.effects_behind)
                    self.kill()
        if self.current_time - self.skill_time_init > 1000 and self.thunder_trap:
            self.thunder_trap = False
            self.user.rooted -= 1
            self.effect_instances.append(
                EffectInstance("thunder_trap", self.user, False, level.current_level.effects_behind)
            )


class HeiLongRedWizardPutFireTrap(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.fire_trap = True

    def load(self):
        super().load()
        self.effect_instances.append(
            EffectInstance("fire_charge", self.user, False, self.user.effects_front)
        )
        sound_player.play("trap")
        self.user.rooted += 1
        self.user.align_xy()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 11000:
            self.kill()
        if self.current_time - self.skill_time_init > 950 and self.fire_trap:
            self.fire_trap = False
            self.effect_instances.append(
                EffectInstance("fire_trap", self.user, False, level.current_level.effects_behind)
            )
            self.user.rooted -= 1
        if self.current_time - self.skill_time_init > 950:
            # 判断玩家是否踩中陷阱
            for to in self.to:
                if to.x == self.user_x and to.y == self.user_y:
                    to.try_damage(1000)
                    EffectInstance("thunder_explode", to, True, to.effects_front)
                    sound_player.play("explode")
                    self.kill()


class FloatingFire(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.flame_charge = True  # 火苗充能
        self.flame_begin = True  # 火苗飞出
        self.flame_end = True  # 火苗到达
        self.to_xy = None  # 火苗目标
        self.delta_x = 0  # 火苗x增量
        self.delta_y = 0  # 火苗y增量
        self.delta_len = 0  # 火苗运行长度
        self.effect_fire = None

    def load(self):
        super().load()
        if len(self.to) > 0:
            to_list = self.to
            self.to = self.to[0]
            dist = abs(to_list[0].x - self.user.x) + abs(to_list[0].y - self.user.y)
            for to in to_list:
                new_dist = abs(to.x - self.user.x) + abs(to.y - self.user.y)
                if new_dist < dist:
                    self.to = to
                    dist = new_dist
        else:
            self.kill()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 3000:
            self.kill()
        if not self.flame_begin and self.flame_end:
            e = self.effect_fire
            if self.delta_len != 0:
                e.set_xy_pos(e.x_pos + 8 * self.delta_x / self.delta_len, e.y_pos + 8 * self.delta_y / self.delta_len)
            if e.x == self.to_xy[0] and e.y == self.to_xy[1]:
                # 飞火到达目的地
                self.flame_end = False
                self.kill()
                sound_player.play("crash")
                # 造成伤害
                if self.to.x == self.to_xy[0] and self.to.y == self.to_xy[1]:
                    if self.real_damage:
                        self.to.real_damage(self.damage_blood)
                    else:
                        self.to.try_damage(self.damage_blood)
                # 引爆糖泡
                bombs = level.current_level.get_bomb_instance(self.to_xy[0], self.to_xy[1])
                if len(bombs) > 0:
                    bombs[0].explode()
        if not self.flame_charge and self.flame_begin:
            self.flame_begin = False
            self.delta_x = self.to_xy[0] - self.user_x
            self.delta_y = self.to_xy[1] - self.user_y
            self.delta_len = sqrt(self.delta_x * self.delta_x + self.delta_y * self.delta_y)
            if self.delta_x > 0:
                self.effect_fire = EffectInstance("floating_fire_r", self.user, False, self.user.effects_front)
            else:
                self.effect_fire = EffectInstance("floating_fire_l", self.user, False, self.user.effects_front)
            self.effect_instances.append(self.effect_fire)

        if self.current_time - self.skill_time_init > 1000 and self.flame_charge:
            # 眩晕爆炸
            self.flame_charge = False
            for e in self.effect_instances:
                e.state = EffectState.DEAD
            self.user.rooted -= 1
        if self.loaded:
            # npc施法阵与眩晕范围提示
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            self.effect_instances.append(
                EffectInstance("launch2", self.user, True, self.user.effects_front)
            )
            sound_player.play("launch")
            self.to_xy = (self.to.x, self.to.y)


class HeroFloatingFire(FloatingFire):

    def __init__(self, user, to, skill_instances):
        self.damage_blood = 1000
        self.real_damage = True
        super().__init__(user, to, skill_instances)


class HeiLongFloatingFire(FloatingFire):

    def __init__(self, user, to, skill_instances):
        self.damage_blood = 1000
        self.real_damage = False
        super().__init__(user, to, skill_instances)


class HeiLongHellDragonDistantFire(HeiLongAbyssDragonDistantFire):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.damage_blood = 500


class HeiLongHellDragonCharge(Skill):

    def __init__(self, user, skill_instances):
        super().__init__(user, None, skill_instances)
        self.loaded = True
        self.smoke = True
        self.cancel_firework = True
        self.effect_firework = None

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 13000:
            self.user.contact -= 500  # 近身伤害复原
            self.kill()
        if self.current_time - self.skill_time_init > 13000 and self.cancel_firework:
            self.cancel_firework = False
            self.effect_firework.state = EffectState.DEAD
        if self.current_time - self.skill_time_init > 3000 and self.smoke:
            self.smoke = False
            self.user.rooted -= 1
            self.user.contact += 500  # 近身伤害增加500
            sound_player.play("launch")
            self.effect_firework = EffectInstance("firework_blue", self.user, True, self.user.effects_front)
            self.effect_instances.append(self.effect_firework)
            for x in range(-2, 3):
                for y in range(-2, 3):
                    an_effect = EffectInstance("smoke", self.user, False, self.user.effects_front)
                    an_effect.set_xy(self.user.x - x, self.user.y - y)
                    self.effect_instances.append(an_effect)
        if self.current_time - self.skill_time_init > 0 and self.loaded:
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            sound_player.play("launch")


class HeiLongHellDragonScope(Skill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)
        self.loaded = True
        self.to_xy = dict()

    def load(self):
        super().load()

    def update(self):
        super().update()
        if self.current_time - self.skill_time_init > 800:
            # 激活必杀技
            self.user.rooted -= 1
            for to in self.to:
                if to.x == self.to_xy[to][0] and to.y == self.to_xy[to][1]:
                    to.try_damage(30000)
            self.kill()
        if self.loaded:
            # npc施法阵与眩晕范围提示
            self.loaded = False
            self.user.rooted += 1
            self.user.align_xy()
            sound_player.play("launch")
            self.effect_instances.append(
                EffectInstance("poison_charge", self.user, False, self.user.effects_front)
            )
            for to in self.to:
                self.to_xy[to] = (to.x, to.y)
                self.effect_instances.append(
                    EffectInstance("scope", to, False, self.user.effects_front)
                )
