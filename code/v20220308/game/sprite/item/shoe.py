import pygame

from game.frame import item
from game.sprite.player import Player
from game.sprite.item_instance import ItemInstance, ItemState


class Shoe(ItemInstance):

    def __init__(self, x, y, dictionary):
        super(Shoe, self).__init__(x, y, dictionary, item.get_item("item3"))

    def player_get(self, p: Player):
        if self.state == ItemState.DEAD:
            return
        max_speed = len(p.hero_json["speed"]) - 1
        p.speed = min(p.speed + 1, max_speed)
        self.switch_state(ItemState.DEAD)
