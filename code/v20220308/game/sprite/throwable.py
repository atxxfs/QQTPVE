import math

from game.const import game as G
from game.level import level
from game.sprite import updatable


def cal_y(a, b, c, x):
    return a * x * x + b * x + c


class Throwable(updatable.Updatable):

    def __init__(self, x, y):

        super(Throwable, self).__init__(x, y)
        self.throwing = False  # 正在被投掷
        self.direction = None  # 抛掷方向 "R" "L"
        self.points = None  # 抛物线上的点
        self.current_point = 0  # 当前在第几个点

    def throw_to(self, to_x, to_y, direction):

        if self.throwing is True:
            return  # 正在投掷的对象 不能再投掷
        if to_x == self.x and to_y == self.y:
            return  # 目标点与当前点重叠 不能再投掷
        cl = level.current_level
        real_x = (to_x + cl.map_x) % cl.map_x
        real_y = (to_y + cl.map_y) % cl.map_y
        if (real_x, real_y) in cl.obstacle_instances:
            if direction == "R":
                self.throw_to(to_x - 1, to_y, "R")
            if direction == "L":
                self.throw_to(to_x + 1, to_y, "L")
            if direction == "U":
                self.throw_to(to_x, to_y + 1, "U")
            if direction == "D":
                self.throw_to(to_x, to_y - 1, "D")
            return
        self.throwing = True
        self.direction = direction
        self.set_restoration(real_x, real_y)

        from_x_pos = self.x_pos
        from_y_pos = self.y_pos
        to_x_pos = to_x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
        to_y_pos = to_y * G.GAME_SQUARE + G.HALF_GAME_SQUARE
        self.get_points((from_x_pos, from_y_pos), (to_x_pos, to_y_pos))

    def get_points(self, p1, p2):

        self.points = list()
        if p1[0] == p2[0]:
            # 竖直抛掷
            now_y = p1[1]
            diff = abs(now_y - p2[1])
            if self.direction == "U":
                while diff > 10:
                    now_y -= 10
                    if diff < 10:
                        now_y = p2[1]
                    if now_y < 0:
                        self.points.append((p1[0], now_y + level.current_level.map_y_pos))
                    else:
                        self.points.append((p1[0], now_y))
                    diff = abs(now_y - p2[1])
            if self.direction == "D":
                while diff > 10:
                    now_y += 10
                    if diff < 10:
                        now_y = p2[1]
                    if now_y > level.current_level.map_y_pos:
                        self.points.append((p1[0], now_y % level.current_level.map_y_pos))
                    else:
                        self.points.append((p1[0], now_y))
                    diff = abs(now_y - p2[1])
        else:
            # 非竖直抛掷
            # 三点式
            # x_abs = abs(self.to_x - self.from_x)
            # y_abs = abs(self.to_y - self.from_y)
            # if y_abs != 0:
            #     p3 = (self.from_x + x_abs + y_abs, self.from_y)
            # else:
            #     p3 = ((self.from_x + self.to_x) / 2, self.from_y - x_abs / 4)
            # b_up = ((p2[0] ** 2 - p3[0] ** 2) * (p1[1] - p2[1])) - ((p1[0] ** 2 - p2[0] ** 2) * (p2[1] - p3[1]))
            # b_down = ((p2[0] ** 2 - p3[0] ** 2) * (p1[0] - p2[0])) - ((p1[0] ** 2 - p2[0] ** 2) * (p2[0] - p3[0]))
            # b = b_up / b_down
            # a = (p1[1] - p2[1] - b * (p1[0] - p2[0])) / (p1[0] ** 2 - p2[0] ** 2)
            # c = p1[1] - a * p1[0] ** 2 - b * p1[0]

            # 两点式
            a = 0.002
            b = (p1[1] - p2[1]) / (p1[0] - p2[0]) - a * (p1[0] + p2[0])
            c = p1[1] - a * p1[0] * p1[0] - b * p1[0]

            now_x = p1[0]
            diff = abs(now_x - p2[0])
            if self.direction == "R":
                while diff > 10:
                    k = 2 * a * now_x + b
                    now_x += 12 / math.sqrt(k * k + 1)
                    if diff < 10:
                        now_x = p2[0]
                    now_y = cal_y(a, b, c, now_x)
                    if now_x > level.current_level.map_x_pos:
                        self.points.append((now_x % level.current_level.map_x_pos, now_y))
                    else:
                        self.points.append((now_x, now_y))
                    diff = abs(now_x - p2[0])

            if self.direction == "L":
                while diff > 10:
                    k = 2 * a * now_x + b
                    now_x -= 12 / math.sqrt(k * k + 1)
                    if diff < 10:
                        now_x = p2[0]
                    now_y = cal_y(a, b, c, now_x)
                    if now_x < 0:
                        self.points.append((now_x + level.current_level.map_x_pos, now_y))
                    else:
                        self.points.append((now_x, now_y))
                    diff = abs(now_x - p2[0])

    def throw(self):

        if self.throwing is False:
            return
        if self.current_point < len(self.points):
            # 正在投掷
            self.x_pos = self.points[self.current_point][0]
            self.y_pos = self.points[self.current_point][1]
            self.current_point += 1
        else:
            # 投掷完毕
            self.throwing = False
            self.direction = None
            self.points = None
            self.current_point = 0
            self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE
            self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE

    def set_restoration(self, to_x, to_y):
        # 子类必须重写 在抛出的一瞬间就要确定xy坐标
        pass
