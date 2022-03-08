from game.frame import item
from game.sprite.player import Player
from game.sprite.item_instance import ItemInstance, ItemState


class Thunder(ItemInstance):

    def __init__(self, x, y, dictionary):
        super(Thunder, self).__init__(x, y, dictionary, item.get_item("item2"))

    def player_get(self, p: Player):
        if self.state == ItemState.DEAD:
            return
        max_power = len(p.hero_json["power"]) - 1
        p.power = min(p.power + 1, max_power)
        self.switch_state(ItemState.DEAD)
