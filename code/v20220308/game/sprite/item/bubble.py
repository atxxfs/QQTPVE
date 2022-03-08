import pygame

from game.frame import item
from game.sprite.player import Player
from game.sprite.item_instance import ItemInstance, ItemState


class Bubble(ItemInstance):

    def __init__(self, x, y, dictionary):
        super(Bubble, self).__init__(x, y, dictionary, item.get_item("item1"))

    def player_get(self, p: Player):
        if self.state == ItemState.DEAD:
            return
        max_bomb_level = len(p.hero_json["bomb"]) - 1
        if p.bomb < max_bomb_level:
            p.bomb += 1
            p.remain_bombs += p.hero_json["bomb"][p.bomb] - p.hero_json["bomb"][p.bomb - 1]

        self.switch_state(ItemState.DEAD)
