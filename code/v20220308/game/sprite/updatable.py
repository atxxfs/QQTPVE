import pygame

from game.const import game as G
from game.level import level


def current_grid(x_pos, y_pos):
    x = x_pos // G.GAME_SQUARE
    y = y_pos // G.GAME_SQUARE
    return int(x), int(y)


class Updatable(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super(Updatable, self).__init__()
        self.x = x
        self.y = y
        self.x_pos = self.x * G.GAME_SQUARE + G.HALF_GAME_SQUARE  # 中心点x坐标
        self.y_pos = self.y * G.GAME_SQUARE + G.HALF_GAME_SQUARE  # 中心点y坐标

    def if_hide(self):
        ret = False
        ois = level.current_level.obstacle_instances
        if (self.x, self.y) in ois.keys():
            an_obstacle = ois[(self.x, self.y)]
            if an_obstacle.obstacle_can_hide:
                self.blank_img()
                ret = True
        return ret

    def blank_img(self):
        # 清空image
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA, 32)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def get_y(self):
        return self.y
