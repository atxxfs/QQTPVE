import enum
import json
import pygame
from game.const import game as G
from game.const import color as C
from game.frame import character
from game.level import level
from game.skill.skill import Protect3s
from game.sound import sound_player
from game.sprite import updatable

shadow = pygame.image.load("res/img/misc/misc131_stand_0_0.png")


class Player(updatable.Updatable):

    def __init__(self, character_name, xy, color=C.CHARACTER_RED):
        super(Player, self).__init__(*xy)

        self.color = color
        self.state = PlayerState.NORMAL
        self.x_old, self.y_old = xy
        self.x_y_changed_trigger = False  # x或y发生变化的标志位

        self.walking = self.walking_old = False
        self.orientation = "D"
        self.orientation_old = ""
        self.update_time_old = pygame.time.get_ticks()  # 上次update的时刻

        self.blood = 0  # 玩家血量
        self.speed = 0  # 玩家移动速度（pixel/ms）
        self.defense = 0  # 玩家防御力
        self.protected = 0  # 正在受金钟罩保护
        self.remain_blood = 0  # 当前玩家剩余血量
        self.district_locked = False  # 当前区域 是否锁住玩家

        self.rooted = 0  # 大于0时定身 方向键无效
        self.rooted_begin = 0  # 时长定身开始时刻ms
        self.rooted_duration = 0  # 时长定身持续时间ms
        self.reverse = 0  # 大于0时反向 方向键倒置
        self.reverse_begin = 0
        self.reverse_duration = 0
        self.can_kick = False  # 可以踢糖泡
        self.skill_names = list()  # 技能名
        self.skill_init_times = list()  # 技能初始可以施放时刻tick
        self.skill_intervals = list()  # 技能冷却时间ms
        self.skill_remains = list()  # 技能剩余次数 -1表示无限
        self.skill_instances = list()  # 玩家当前技能
        self.effects_behind = list()
        self.effects_front = list()

        self.character = None
        self.character_timer = pygame.time.get_ticks()
        self.character_interval = 0
        self.character_frame_idx = 0
        self.character_frame_trigger = False  # 重新显示character的标志位
        self.cx = self.cy = 0  # character显示的偏移
        self.STAND = ""
        self.text_font = pygame.font.Font("res/font/century.ttf", 12)
        self.text_img = None
        self.text_init_time = 0
        self.text_duration = 0

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()

    def load_character(self, character_name, color):
        # 加载角色character
        with open("game/frame/character/" + character_name + ".json") as f:
            character_json = json.load(f)
        self.character_interval = character_json["INTERVAL"]
        return character.get_character(character_json, color)

    def align_xy(self):
        # 标齐当前xy 用于npc和玩家施法立正
        self.set_xy(self.x, self.y)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        self.x_pos = x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
        self.y_pos = y * G.GAME_SQUARE + G.HALF_GAME_SQUARE

    def set_motion(self, motion=None):
        # 设置人物运动状态motion 可以是R U L D None
        if motion is None or motion == "None" or self.speed == 0:
            self.walking = False
            return
        if self.rooted > 0:
            return
        if self.reverse > 0:
            if motion == "U":
                motion = "D"
            elif motion == "D":
                motion = "U"
            elif motion == "L":
                motion = "R"
            elif motion == "R":
                motion = "L"
        self.walking = True
        self.orientation = motion

    def set_text(self, text, duration):
        self.text_img = self.text_font.render(text, True, G.PLAYER_TEXT_COLOR)
        self.text_init_time = pygame.time.get_ticks()
        self.text_duration = duration

    def stimulate_character_frame_trigger(self):
        # 判断运动状态是否发生改变，每一帧都必须调用，修改trigger值，并更新old值
        if self.orientation_old != self.orientation or self.walking_old != self.walking:
            self.character_frame_trigger = True
        else:
            self.character_frame_trigger = False
        self.orientation_old = self.orientation
        self.walking_old = self.walking

    def stimulate_x_y_changed_trigger(self):
        # 判断x或y坐标发生变化的标志，每一帧都必须调用，修改trigger值，并更新old值
        if self.x != self.x_old or self.y != self.y_old:
            self.x_y_changed_trigger = True
        else:
            self.x_y_changed_trigger = False
        self.x_old = self.x
        self.y_old = self.y

    def update(self):

        current_time = pygame.time.get_ticks()
        if self.state == PlayerState.NORMAL:
            self.stimulate_x_y_changed_trigger()
            self.update_frame(current_time)
            self.update_pos()
            self.if_obstacle_trigger()
            self.if_take_item()
            self.grid_damage(current_time)
            self.check_rooted_time(current_time)
            self.check_reverse_time(current_time)
        if self.state == PlayerState.LOSE:
            self.update_frame_dead(current_time)
        self.update_skills()
        self.update_effects()
        self.stimulate_character_frame_trigger()
        self.update_time_old = current_time

    def update_skills(self):
        for s in self.skill_instances:
            s.update()

    def update_effects(self):
        # 刷新玩家技能
        for e in self.effects_behind:
            e.update()
        for e in self.effects_front:
            e.update()

    def update_frame(self, current_time):

        if self.character_frame_trigger or current_time - self.character_timer > self.character_interval:
            # 如果 (1)时间到 或 (2)运动发生改变 则切换帧
            STAND = ""
            if not self.walking:
                STAND = "STAND_"
            self.STAND = STAND
            LEN = self.character[STAND + self.orientation]["Len"]
            self.cx = self.character[STAND + self.orientation]["Cx"]
            self.cy = self.character[STAND + self.orientation]["Cy"]
            self.character_frame_idx = (self.character_frame_idx + 1) % LEN
            self.character_timer = current_time
        self.rect.x = self.x_pos + self.cx
        self.rect.y = self.y_pos + self.cy
        # 注意 self.image是每隔INTERVAL更新一次 而self.rect的x,y是每帧更新一次

    def update_frame_dead(self, current_time):
        if current_time - self.character_timer > 200:
            LEN = self.character["LOSE"]["Len"]
            self.cx = self.character["LOSE"]["Cx"]
            self.cy = self.character["LOSE"]["Cy"]
            self.character_frame_idx = (self.character_frame_idx + 1) % LEN
            self.character_timer = current_time
        self.rect.x = self.x_pos + self.cx
        self.rect.y = self.y_pos + self.cy

    def update_pos(self):

        if self.rooted > 0:
            self.set_motion()

        if self.walking:
            speed = self.speed * (pygame.time.get_ticks() - self.update_time_old)  # self.speed 是每毫秒的移动步长，要乘上time
            speed = min(20, speed)  # 防止卡进墙壁里
            right = self.x_pos + G.HALF_GAME_SQUARE - 1
            right_grid = int(right // G.GAME_SQUARE)
            top = self.y_pos - G.HALF_GAME_SQUARE
            top_grid = int(top // G.GAME_SQUARE)
            left = self.x_pos - G.HALF_GAME_SQUARE
            left_grid = int(left // G.GAME_SQUARE)
            bottom = self.y_pos + G.HALF_GAME_SQUARE - 1
            bottom_grid = int(bottom // G.GAME_SQUARE)
            cl = level.current_level
            block = cl.block
            if self.orientation == "R":
                if right // G.GAME_SQUARE != (right + speed) // G.GAME_SQUARE:  # 右侧身位跨格子时
                    right_screen = right + speed >= cl.map_x_pos  # 右侧碰撞屏幕
                    right_district = self.x_pos + speed >= cl.district_square["x2"]
                    right_block = block[1][self.x + 1][self.y]  # 右侧numpy障碍
                    right_block_top_0 = self.y != top // G.GAME_SQUARE and block[0][self.x + 1][top_grid + 1]  # 右上侧横向障碍
                    right_block_top_1 = block[1][self.x + 1][top_grid]  # 右上侧纵向障碍
                    right_block_bottom_0 = self.y != bottom // G.GAME_SQUARE and block[0][self.x + 1][bottom_grid]  # 右下侧横向障碍
                    right_block_bottom_1 = block[1][self.x + 1][bottom_grid]  # 右下侧纵向障碍
                    right_edge = (right + speed) // G.GAME_SQUARE
                    right_bomb = len(cl.get_bomb_instance(right_edge, self.y))  # 右侧糖泡
                    right_bomb_top = len(cl.get_bomb_instance(right_edge, top_grid))  # 右上侧糖泡
                    right_bomb_bottom = len(cl.get_bomb_instance(right_edge, bottom_grid))  # 右下侧糖泡
                    if self.can_kick and not right_block:
                        if right_bomb == 1:
                            b = cl.get_bomb_instance(right_edge, self.y)[0]
                            b.throw_to(b.x + 8, b.y, "R")
                            sound_player.play("kick")
                        elif right_bomb_top == 1:
                            b = cl.get_bomb_instance(right_edge, top_grid)[0]
                            b.throw_to(b.x + 8, b.y, "R")
                            sound_player.play("kick")
                        elif right_bomb_bottom == 1:
                            b = cl.get_bomb_instance(right_edge, bottom_grid)[0]
                            b.throw_to(b.x + 8, b.y, "R")
                            sound_player.play("kick")
                    if self.district_locked and right_district:
                        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                        self.collide_district()
                    elif right_block > 0 or right_screen or right_bomb > 0:
                        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                    elif right_block_top_0 > 0 or right_block_top_1 > 0 or right_bomb_top > 0:
                        self.y_pos = min(self.y_pos + speed, self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    elif right_block_bottom_0 > 0 or right_block_bottom_1 > 0 or right_bomb_bottom > 0:
                        self.y_pos = max(self.y_pos - speed, self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    else:
                        self.x_pos += speed
                        cl.scroll_map()
                elif self.x_pos // G.GAME_SQUARE != (self.x_pos + speed) // G.GAME_SQUARE:
                    if len(level.current_level.get_bomb_instance(self.x + 1, self.y)) == 0:
                        self.x_pos += speed
                        cl.scroll_map()
                else:
                    self.x_pos += speed
                    cl.scroll_map()
            if self.orientation == "U":
                if top // G.GAME_SQUARE != (top - speed) // G.GAME_SQUARE:
                    top_screen = top - speed < 0
                    top_district = self.y_pos - speed < cl.district_square["y1"]
                    top_block = block[0][self.x][self.y]
                    top_block_left_0 = block[0][left_grid][self.y]
                    top_block_left_1 = self.x != left // G.GAME_SQUARE and block[1][left_grid + 1][self.y - 1]
                    top_block_right_0 = block[0][right_grid][self.y]
                    top_block_right_1 = self.x != right // G.GAME_SQUARE and block[1][right_grid][self.y - 1]
                    top_edge = (top - speed) // G.GAME_SQUARE
                    top_bomb = len(cl.get_bomb_instance(self.x, top_edge))
                    top_bomb_left = len(cl.get_bomb_instance(left_grid, top_edge))
                    top_bomb_right = len(cl.get_bomb_instance(right_grid, top_edge))
                    if self.can_kick and not top_block:
                        if top_bomb == 1:
                            b = cl.get_bomb_instance(self.x, top_edge)[0]
                            b.throw_to(b.x, b.y - 8, "U")
                            sound_player.play("kick")
                        elif top_bomb_left == 1:
                            b = cl.get_bomb_instance(left_grid, top_edge)[0]
                            b.throw_to(b.x, b.y - 8, "U")
                            sound_player.play("kick")
                        elif top_bomb_right == 1:
                            b = cl.get_bomb_instance(right_grid, top_edge)[0]
                            b.throw_to(b.x, b.y - 8, "U")
                            sound_player.play("kick")
                    if self.district_locked and top_district:
                        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                        self.collide_district()
                    elif top_block > 0 or top_screen or top_bomb > 0:
                        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                    elif top_block_left_0 > 0 or top_block_left_1 > 0 or top_bomb_left > 0:
                        self.x_pos = min(self.x_pos + speed, self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    elif top_block_right_0 > 0 or top_block_right_1 > 0 or top_bomb_right > 0:
                        self.x_pos = max(self.x_pos - speed, self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    else:
                        self.y_pos -= speed
                        cl.scroll_map()
                elif self.y_pos // G.GAME_SQUARE != (self.y_pos - speed) // G.GAME_SQUARE:
                    if len(level.current_level.get_bomb_instance(self.x, self.y - 1)) == 0:
                        self.y_pos -= speed
                        cl.scroll_map()
                else:
                    self.y_pos -= speed
                    cl.scroll_map()
            if self.orientation == "L":
                if left // G.GAME_SQUARE != (left - speed) // G.GAME_SQUARE:
                    left_screen = left - speed < 0
                    left_district = self.x_pos - speed < cl.district_square["x1"]
                    left_block = block[1][self.x][self.y]
                    left_block_top_0 = self.y != top // G.GAME_SQUARE and block[0][self.x - 1][top_grid + 1]
                    left_block_top_1 = block[1][self.x][top_grid]
                    left_block_bottom_0 = self.y != bottom // G.GAME_SQUARE and block[0][self.x - 1][bottom_grid]
                    left_block_bottom_1 = block[1][self.x][bottom_grid]
                    left_edge = (left - speed) // G.GAME_SQUARE
                    left_bomb = len(cl.get_bomb_instance(left_edge, self.y))
                    left_bomb_top = len(cl.get_bomb_instance(left_edge, top_grid))
                    left_bomb_bottom = len(cl.get_bomb_instance(left_edge, bottom_grid))
                    if self.can_kick and not left_block:
                        if left_bomb == 1:
                            b = cl.get_bomb_instance(left_edge, self.y)[0]
                            b.throw_to(b.x - 8, b.y, "L")
                            sound_player.play("kick")
                        elif left_bomb_top == 1:
                            b = cl.get_bomb_instance(left_edge, top_grid)[0]
                            b.throw_to(b.x - 8, b.y, "L")
                            sound_player.play("kick")
                        elif left_bomb_bottom == 1:
                            b = cl.get_bomb_instance(left_edge, bottom_grid)[0]
                            b.throw_to(b.x - 8, b.y, "L")
                            sound_player.play("kick")
                    if self.district_locked and left_district:
                        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                        self.collide_district()
                    elif left_block > 0 or left_screen or left_bomb > 0:
                        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                    elif left_block_top_1 > 0 or left_block_top_0 > 0 or left_bomb_top > 0:
                        self.y_pos = min(self.y_pos + speed, self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    elif left_block_bottom_1 > 0 or left_block_bottom_0 > 0 or left_bomb_bottom > 0:
                        self.y_pos = max(self.y_pos - speed, self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    else:
                        self.x_pos -= speed
                        cl.scroll_map()
                elif self.x_pos // G.GAME_SQUARE != (self.x_pos - speed) // G.GAME_SQUARE:
                    if len(level.current_level.get_bomb_instance(self.x - 1, self.y)) == 0:
                        self.x_pos -= speed
                        cl.scroll_map()
                else:
                    self.x_pos -= speed
                    cl.scroll_map()
            if self.orientation == "D":
                if bottom // G.GAME_SQUARE != (bottom + speed) // G.GAME_SQUARE:
                    bottom_block = block[0][self.x][self.y + 1]
                    bottom_district = self.y_pos + speed >= cl.district_square["y2"]
                    bottom_block_right_0 = block[0][int(right // G.GAME_SQUARE)][self.y + 1]
                    bottom_block_right_1 = self.x != right // G.GAME_SQUARE and block[1][int(right // G.GAME_SQUARE)][self.y + 1]
                    bottom_block_left_0 = block[0][int(left // G.GAME_SQUARE)][self.y + 1]
                    bottom_block_left_1 = self.x != left // G.GAME_SQUARE and block[1][int(left // G.GAME_SQUARE) + 1][self.y + 1]
                    bottom_screen = bottom + speed >= cl.map_y_pos
                    bottom_edge = (bottom + speed) // G.GAME_SQUARE
                    bottom_bomb = len(cl.get_bomb_instance(self.x, bottom_edge))
                    bottom_bomb_left = len(cl.get_bomb_instance(left_grid, bottom_edge))
                    bottom_bomb_right = len(cl.get_bomb_instance(right_grid, bottom_edge))
                    if self.can_kick and not bottom_block:
                        if bottom_bomb == 1:
                            b = cl.get_bomb_instance(self.x, bottom_edge)[0]
                            b.throw_to(b.x, b.y + 8, "D")
                            sound_player.play("kick")
                        elif bottom_bomb_left == 1:
                            b = cl.get_bomb_instance(left_grid, bottom_edge)[0]
                            b.throw_to(b.x, b.y + 8, "D")
                            sound_player.play("kick")
                        elif bottom_bomb_right == 1:
                            b = cl.get_bomb_instance(right_grid, bottom_edge)[0]
                            b.throw_to(b.x, b.y + 8, "D")
                            sound_player.play("kick")
                    if self.district_locked and bottom_district:
                        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                        self.collide_district()
                    elif bottom_block > 0 or bottom_screen or bottom_bomb > 0:
                        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
                        self.collide_wall()
                    elif bottom_block_right_0 > 0 or bottom_block_right_1 > 0 or bottom_bomb_right > 0:
                        self.x_pos = max(self.x_pos - speed, self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    elif bottom_block_left_0 > 0 or bottom_block_left_1 > 0 or bottom_bomb_left > 0:
                        self.x_pos = min(self.x_pos + speed, self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE)
                    else:
                        self.y_pos += speed
                        cl.scroll_map()
                elif self.y_pos // G.GAME_SQUARE != (self.y_pos + speed) // G.GAME_SQUARE:
                    if len(level.current_level.get_bomb_instance(self.x, self.y + 1)) == 0:
                        self.y_pos += speed
                        cl.scroll_map()
                else:
                    self.y_pos += speed
                    cl.scroll_map()
        self.x, self.y = updatable.current_grid(self.x_pos, self.y_pos)

    def if_obstacle_trigger(self):
        # 判断player是否激活障碍
        if self.x_y_changed_trigger is not True:
            return  # 必须在xy发生变化的那一帧激活障碍
        ois = level.current_level.obstacle_instances
        if (self.x, self.y) in ois.keys():
            an_obstacle = ois[(self.x, self.y)]
            if an_obstacle.obstacle_trigger:
                an_obstacle.trigger()

    def if_take_item(self):
        # player获取item
        if self.x_y_changed_trigger is not True:
            return
        if (self.x, self.y) in level.current_level.item_instances:
            level.current_level.item_instances[(self.x, self.y)].player_get(self)

    def grid_damage(self, current_time):
        # 每一帧都尝试吸收当前地板上的伤害，如果时间值相同（在同一帧），则造成伤害
        point = (self.x, self.y)
        cl = level.current_level
        if cl.grid_damage_frame and current_time - cl.grid_damage_time[point] < cl.accumulation_time:
            self.try_damage(cl.grid_damage_blood[point])

    def try_damage(self, damage_blood: int, direction="C"):
        if self.state != PlayerState.NORMAL:
            return
        if self.protected > 0:
            return
        if damage_blood > self.defense:
            self.real_damage(damage_blood - self.defense)

    def real_damage(self, damage_blood: int):
        # 真实对玩家扣减damage_blood血量
        self.remain_blood -= damage_blood
        if self.remain_blood <= 0:
            # 角色死亡
            self.remain_blood = 0
            self.switch_state(PlayerState.LOSE)
            self.die()
            return
        Protect3s(self, self.skill_instances)
        if damage_blood > 0:
            self.set_text("HP-" + str(damage_blood), 2000)

    def die(self):
        # 子类重写死亡方法
        pass

    def revive(self, heal_blood: int):
        # 人物复活
        self.switch_state(PlayerState.NORMAL)
        self.heal(heal_blood)
        self.real_damage(0)

    def heal(self, heal_blood: int):
        # 血量恢复
        self.remain_blood = min(self.blood, self.remain_blood + heal_blood)

    def rooted_for(self, duration):
        if self.rooted_begin == 0:
            self.rooted += 1
        self.rooted_begin = pygame.time.get_ticks()
        self.rooted_duration = duration

    def check_rooted_time(self, current_time):
        if self.rooted_begin != 0 and current_time - self.rooted_begin > self.rooted_duration:
            self.rooted -= 1
            self.rooted_begin = 0

    def reverse_for(self, duration):
        if self.reverse_begin != 0:
            return
        self.reverse += 1
        self.reverse_begin = pygame.time.get_ticks()
        self.reverse_duration = duration

    def check_reverse_time(self, current_time):
        if self.reverse_begin != 0 and current_time - self.reverse_begin > self.reverse_duration:
            self.reverse -= 1
            self.reverse_begin = 0

    def collide_wall(self):
        # Player碰撞墙体（包括糖泡）
        pass

    def collide_district(self):
        # Player碰撞区域边界
        pass

    def switch_state(self, new_state):
        # 切换到指定状态 并重置帧索引
        self.state = new_state
        self.character_frame_idx = 0
        self.character_frame_trigger = True
        if new_state == PlayerState.LOSE:
            for s in self.skill_instances:
                self.skill_instances.remove(s)

    def get_y(self):
        return self.y + 0.1

    def draw(self, screen: pygame.Surface):
        # 如果人物隐藏，则不绘图
        display = not super().if_hide()

        if display:
            # 显示背景特效
            for s in self.effects_behind:
                s.draw(screen)
            # 显示阴影
            screen.blit(shadow, (self.x_pos - 17, self.y_pos - 7))
            if self.state == PlayerState.NORMAL:
                for component in character.CHARACTER_COMPONENTS[self.orientation]:
                    if component not in self.character[self.STAND + self.orientation]:
                        continue
                    frame = self.character[self.STAND + self.orientation][component][self.character_frame_idx]
                    screen.blit(frame.image, (frame.cx + self.x_pos + self.cx, frame.cy + self.y_pos + self.cy))
            elif self.state == PlayerState.LOSE and "LOSE" in self.character:
                for component in character.CHARACTER_COMPONENTS[self.orientation]:
                    if component not in self.character["LOSE"]:
                        continue
                    frame = self.character["LOSE"][component][self.character_frame_idx]
                    screen.blit(frame.image, (frame.cx + self.x_pos + self.cx, frame.cy + self.y_pos + self.cy))
        # 显示前景特效
        for s in self.effects_front:
            s.draw(screen)
        # 显示文字
        if pygame.time.get_ticks() - self.text_init_time < self.text_duration:
            screen.blit(self.text_img, (self.x_pos - G.HALF_GAME_SQUARE, self.y_pos - G.GAME_SQUARE - G.GAME_SQUARE))


class PlayerState(enum.Enum):

    NORMAL = 0
    WIN = 1
    LOSE = -1
