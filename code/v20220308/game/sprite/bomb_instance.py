import enum
import pygame

from game.const import game as G
from game.frame import flame
from game.level import level
from game.sound import sound_player
from game.sprite.flame_instance import FlameInstance, FlameType
from game.sprite.throwable import Throwable


def get_type(at, length):
    if length == 1:
        return FlameType.END_INSTANT
    if at == length:
        return FlameType.END_DELAYED
    half_length = length // 2
    if at == half_length:
        return FlameType.MID_THROUGH
    elif at < half_length:
        return FlameType.MID_INSTANT
    else:
        return FlameType.MID_DELAYED
    

class BombInstance(Throwable):

    sound_played = False  # 当前帧播放了爆炸音效 不再重复播放（每帧会重置为False）

    def __init__(self, x, y, bomb_instances_list: list, bomb, power, damage, player=None):

        super(BombInstance, self).__init__(x, y)

        self.bomb = bomb  # 糖泡帧动画
        self.power = power  # 糖泡威力（爆炸长度）
        self.damage = damage  # 糖泡单倍伤害
        self.player = player
        self.bomb_instances_list: list = bomb_instances_list

        self.state = BombState.NORMAL

        self.bomb_timer = 0  # bomb帧计时器
        self.bomb_frame_idx = 0  # bomb帧索引
        self.cx = self.cy = 0  # bomb显示的偏移

        self.bomb_timer_alive = pygame.time.get_ticks()  # bomb存活时间计时器
        self.bomb_timer_explode = None  # bomb爆炸时刻
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.setup()
        self.update()

    def setup(self):
        self.bomb_instances_list.append(self)
        level.current_level.recal_npc_paths = True

    def update(self):

        if self.state == BombState.DEAD:
            return
        current_time = pygame.time.get_ticks()
        if self.state == BombState.NORMAL:
            self.throw()
            self.update_frame(current_time)
            self.update_to_explode(current_time)
            self.if_hide()

    def update_frame(self, current_time):

        if self.state == BombState.NORMAL and current_time - self.bomb_timer > self.bomb["INTERVAL"]:
            LEN = len(self.bomb["STAND"])
            self.bomb_frame_idx = (self.bomb_frame_idx + 1) % LEN
            self.cx = self.bomb["STAND"][self.bomb_frame_idx].cx
            self.cy = self.bomb["STAND"][self.bomb_frame_idx].cy
            self.bomb_timer = current_time
            self.image = self.bomb["STAND"][self.bomb_frame_idx].image
        self.rect.x = self.x_pos - G.HALF_GAME_SQUARE + self.bomb["STAND"][self.bomb_frame_idx].cx
        self.rect.y = self.y_pos - G.HALF_GAME_SQUARE + self.bomb["STAND"][self.bomb_frame_idx].cy

    def update_to_explode(self, current_time):
        if current_time - self.bomb_timer_alive > G.BOMB_EXPLODE_TIME:
            self.explode()

    def switch_state(self, new_state):
        # 切换到指定状态 并重置帧索引
        self.state = new_state
        self.bomb_frame_idx = 0
        if new_state == BombState.DEAD:
            self.uninstall()

    def get_explode_length(self, point, direction, current_len, max_len):
        # 用递归去探测糖泡爆炸动画的长度
        if current_len >= max_len:
            return 0
        cl = level.current_level
        block = cl.block
        ois = cl.obstacle_instances
        if direction == "R":
            next_point = (point[0] + 1, point[1])
            if next_point[0] >= cl.map_x:
                return 0
            if block[1][next_point[0]][next_point[1]] > 0:
                if next_point in ois.keys():
                    an_obstacle = ois[next_point]
                    if an_obstacle.obstacle["BREAKABLE"]:
                        return 1
                return 0
            return 1 + self.get_explode_length(next_point, "R", current_len + 1, max_len)
        if direction == "U":
            next_point = (point[0], point[1] - 1)
            if next_point[1] < 0:
                return 0
            if block[0][next_point[0]][next_point[1] + 1] > 0:
                if next_point in ois.keys():
                    an_obstacle = ois[next_point]
                    if an_obstacle.obstacle["BREAKABLE"]:
                        return 1
                return 0
            return 1 + self.get_explode_length(next_point, "U", current_len + 1, max_len)
        if direction == "L":
            next_point = (point[0] - 1, point[1])
            if next_point[0] < 0:
                return 0
            if block[1][next_point[0] + 1][next_point[1]] > 0:
                if next_point in ois.keys():
                    an_obstacle = ois[next_point]
                    if an_obstacle.obstacle["BREAKABLE"]:
                        return 1
                return 0
            return 1 + self.get_explode_length(next_point, "L", current_len + 1, max_len)
        if direction == "D":
            next_point = (point[0], point[1] + 1)
            if next_point[1] >= cl.map_y:
                return 0
            if block[0][next_point[0]][next_point[1]] > 0:
                if next_point in ois.keys():
                    an_obstacle = ois[next_point]
                    if an_obstacle.obstacle["BREAKABLE"]:
                        return 1
                return 0
            return 1 + self.get_explode_length(next_point, "D", current_len + 1, max_len)

    def explode(self):
        # 引爆自身
        if self.state != BombState.NORMAL:
            return
        if self.throwing:
            return  # 正在抛掷的糖泡不能引爆
        self.switch_state(BombState.DEAD)
        self.bomb_timer_explode = pygame.time.get_ticks()
        if not BombInstance.sound_played:
            sound_player.play("flame")
            BombInstance.sound_played = True

        cl = level.current_level
        ois = cl.obstacle_instances
        fis = cl.flame_instances
        point = (self.x, self.y)
        f = flame.get_flame("FLAME_C")
        if point in ois.keys():
            ois[point].die()
        a_flame = FlameInstance(*point, f, 0)
        fis.append(a_flame)
        for b in cl.get_bomb_instance(*point):  # 尝试引爆其他糖泡
            b.explode()
        if "C" not in cl.grid_damage_orientations[point]:
            cl.grid_damage_orientations[point].add("C")
            if self.bomb_timer_explode - cl.grid_damage_time[point] < cl.accumulation_time:
                cl.grid_damage_blood[point] += self.damage
            else:
                cl.grid_damage_blood[point] = self.damage
                cl.grid_damage_time[point] = self.bomb_timer_explode

        len = self.get_explode_length((self.x, self.y), "R", 0, self.power)
        distance = range(1, len + 1)
        for i in distance:  # 向右爆炸延伸
            point = (self.x + i, self.y)
            if point in ois.keys():  # 尝试摧毁障碍
                ois[point].die()
            f = flame.get_flame("FLAME_R")
            a_flame = FlameInstance(*point, f, get_type(i, len))  # 生成动画
            fis.append(a_flame)
            for b in cl.get_bomb_instance(*point):  # 尝试引爆其他糖泡
                b.explode()
            if "R" not in cl.grid_damage_orientations[point]:
                cl.grid_damage_orientations[point].add("R")
                if self.bomb_timer_explode - cl.grid_damage_time[point] < cl.accumulation_time:
                    cl.grid_damage_blood[point] += self.damage
                else:
                    cl.grid_damage_blood[point] = self.damage
                    cl.grid_damage_time[point] = self.bomb_timer_explode

        len = self.get_explode_length((self.x, self.y), "U", 0, self.power)
        distance = range(1, len + 1)
        for i in distance:
            point = (self.x, self.y - i)
            if point in ois.keys():
                ois[point].die()
            f = flame.get_flame("FLAME_U")
            a_flame = FlameInstance(*point, f, get_type(i, len))
            fis.append(a_flame)
            for b in cl.get_bomb_instance(*point):  # 尝试引爆其他糖泡
                b.explode()
            if "U" not in cl.grid_damage_orientations[point]:
                cl.grid_damage_orientations[point].add("U")
                if self.bomb_timer_explode - cl.grid_damage_time[point] < cl.accumulation_time:
                    cl.grid_damage_blood[point] += self.damage
                else:
                    cl.grid_damage_blood[point] = self.damage
                    cl.grid_damage_time[point] = self.bomb_timer_explode

        len = self.get_explode_length((self.x, self.y), "L", 0, self.power)
        distance = range(1, len + 1)
        for i in distance:
            point = (self.x - i, self.y)
            if point in ois.keys():
                ois[point].die()
            f = flame.get_flame("FLAME_L")
            a_flame = FlameInstance(*point, f, get_type(i, len))
            fis.append(a_flame)
            for b in cl.get_bomb_instance(*point):  # 尝试引爆其他糖泡
                b.explode()
            if "L" not in cl.grid_damage_orientations[point]:
                cl.grid_damage_orientations[point].add("L")
                if self.bomb_timer_explode - cl.grid_damage_time[point] < cl.accumulation_time:
                    cl.grid_damage_blood[point] += self.damage
                else:
                    cl.grid_damage_blood[point] = self.damage
                    cl.grid_damage_time[point] = self.bomb_timer_explode

        len = self.get_explode_length((self.x, self.y), "D", 0, self.power)
        distance = range(1, len + 1)
        for i in distance:
            point = (self.x, self.y + i)
            if point in ois.keys():
                ois[point].die()
            f = flame.get_flame("FLAME_D")
            a_flame = FlameInstance(*point, f, get_type(i, len))
            fis.append(a_flame)
            for b in cl.get_bomb_instance(*point):  # 尝试引爆其他糖泡
                b.explode()
            if "D" not in cl.grid_damage_orientations[point]:
                cl.grid_damage_orientations[point].add("D")
                if self.bomb_timer_explode - cl.grid_damage_time[point] < cl.accumulation_time:
                    cl.grid_damage_blood[point] += self.damage
                else:
                    cl.grid_damage_blood[point] = self.damage
                    cl.grid_damage_time[point] = self.bomb_timer_explode

        cl.grid_damage_frame = True

    def set_restoration(self, to_x, to_y):
        self.x = to_x
        self.y = to_y

    def uninstall(self):
        self.bomb_instances_list.remove(self)
        level.current_level.recal_npc_paths = True
        if self.player is not None:
            self.player.restore_a_bomb()


class BombState(enum.Enum):
    DEAD = -1
    NORMAL = 0

