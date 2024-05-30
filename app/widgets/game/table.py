import pygame
import pygame.gfxdraw

from math import sin, cos, pi

from app.shared import load_image
from app.widgets.widget import Widget


class Table(Widget):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)
        self._image = load_image("assets/sprites/misc/table.png", self.rect.size)

    def get_edge_coords(self, degrees: float, scale=(1.0, 1.0)):
        rad = degrees / 180 * pi
        x, y = self.rect.center
        rx, ry = scale[0] * self.rect.width / 2, scale[1] * self.rect.height / 2

        return x + rx * cos(rad), y + ry * sin(rad)
