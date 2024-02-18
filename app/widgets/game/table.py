import pygame
import pygame.gfxdraw

from math import sin, cos, pi


class Table(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load("assets/sprites/misc/table.png"), dimensions)
        self.rect = self.image.get_rect(center=pos)

    def get_edge_coords(self, degrees: float, scale=(1.0, 1.0)):
        rad = degrees / 180 * pi
        x, y = self.rect.center
        rx, ry = scale[0] * self.rect.width / 2, scale[1] * self.rect.height / 2

        return x + rx * cos(rad), y + ry * sin(rad)
