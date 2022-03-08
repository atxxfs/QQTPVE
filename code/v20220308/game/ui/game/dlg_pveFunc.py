import pygame
from game.ui.ui import UIInstance


class DlgPveFunc(UIInstance):

    def __init__(self):
        super().__init__("game", "dlg_pveFunc")
        self.rect.x = 619
        self.rect.y = 537

