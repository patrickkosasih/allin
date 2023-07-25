import pygame
import pygame.gfxdraw


class Table(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load("assets/sprites/table.png"), dimensions)
        self.rect = self.image.get_rect(center=pos)

