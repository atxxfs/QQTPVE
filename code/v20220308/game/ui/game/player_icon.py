import pygame


class PlayerIcon(pygame.sprite.Sprite):

    def __init__(self, name):
        self.image = pygame.image.load("res/img/ui/game/" + name + ".png")
        self.rect = self.image.get_rect()
        self.rect.y = 78

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
