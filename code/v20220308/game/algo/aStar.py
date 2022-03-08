from queue import PriorityQueue
from game.level import level


def r_block(x, y):
    return level.current_level.block[1][x + 1][y] > 0


def u_block(x, y):
    return level.current_level.block[0][x][y] > 0


def l_block(x, y):
    return level.current_level.block[1][x][y] > 0


def d_block(x, y):
    return level.current_level.block[0][x][y + 1] > 0


def bomb_exist(x, y):
    return len(level.current_level.get_bomb_instance(x, y)) > 0


def can_reach_r(x, y):
    return not r_block(x, y) and not bomb_exist(x + 1, y)


def can_reach_u(x, y):
    return not u_block(x, y) and not bomb_exist(x, y - 1)


def can_reach_l(x, y):
    return not l_block(x, y) and not bomb_exist(x - 1, y)


def can_reach_d(x, y):
    return not d_block(x, y) and not bomb_exist(x, y + 1)


def neighbors(current, npc_grid, limit1, limit2):
    # 计算四个邻位是否可达
    points = []
    x, y = current  # 当前坐标
    x1, y1 = limit1  # 区域左上角坐标
    x2, y2 = limit2  # 区域右下角坐标
    if heuristic(current, npc_grid) == 1 and bomb_exist(*npc_grid):
        if not r_block(x, y) and x + 1 <= x2:
            points.append((x + 1, y))
        if not u_block(x, y) and y - 1 >= y1:
            points.append((x, y - 1))
        if not l_block(x, y) and x - 1 >= x1:
            points.append((x - 1, y))
        if not d_block(x, y) and y + 1 <= y2:
            points.append((x, y + 1))
    else:
        if can_reach_r(x, y) and x + 1 <= x2:
            points.append((x + 1, y))
        if can_reach_u(x, y) and y - 1 >= y1:
            points.append((x, y - 1))
        if can_reach_l(x, y) and x - 1 >= x1:
            points.append((x - 1, y))
        if can_reach_d(x, y) and y + 1 <= y2:
            points.append((x, y + 1))
    return points


def heuristic(next, npc_grid):
    x1, y1 = next
    x2, y2 = npc_grid
    return abs(x1 - x2)**2 + abs(y1 - y2)**2


def reverse(came_from, hero_grid, npc_grid):
    go_to = dict()
    while hero_grid != npc_grid:
        if hero_grid not in came_from.keys():
            break
        go_to[came_from[hero_grid]] = hero_grid
        hero_grid = came_from[hero_grid]
    return go_to


def cal_path(npc_grid, hero_grid, limit1, limit2):
    # limit1 区域左上角
    # limit2 区域右下角
    frontier = PriorityQueue()
    frontier.put((0, npc_grid))
    came_from = dict()
    cost_so_far = dict()
    came_from[npc_grid] = None
    cost_so_far[npc_grid] = 0

    while not frontier.empty():

        current = frontier.get()[1]

        if current == hero_grid:
            break

        for next in neighbors(current, npc_grid, limit1, limit2):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, hero_grid)
                frontier.put((priority, next))
                came_from[next] = current

    return reverse(came_from, hero_grid, npc_grid)
