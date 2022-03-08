import pygame


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy

    def duplicate(self):
        img = self.image.copy()
        return Frame(img, self.cx, self.cy)
