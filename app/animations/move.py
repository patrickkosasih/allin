import pygame.sprite
from pygame.math import Vector2

from app.animations.animation import Animation
from app.animations.interpolations import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.widgets.widget import Widget


class MoveAnimation(Animation):
    def __init__(self, duration, sprite: "Widget",
                 start_pos: tuple or Vector2 or None, end_pos: tuple or Vector2,
                 unit="px", anchor="tl", pivot="ctr",
                 **kwargs):
        super().__init__(duration, **kwargs)

        self.sprite = sprite
        self.start_pos = Vector2(start_pos) if start_pos else Vector2(self.sprite.rect.center)
        self.end_pos = Vector2(end_pos)

        self.unit = unit
        self.anchor = anchor
        self.pivot = pivot

    def update_anim(self):
        current_pos = self.start_pos + self.interpol_phase * (self.end_pos - self.start_pos)

        try:
            self.sprite.set_pos(*current_pos, self.unit, self.anchor, self.pivot)
        except AttributeError:  # TODO Remove after all widgets have been updated.
            self.sprite.rect = self.sprite.image.get_rect(center=current_pos)

    def finish(self):
        try:
            self.sprite.set_pos(*self.end_pos, self.unit, self.anchor, self.pivot)
        except AttributeError:  # TODO Remove after all widgets have been updated.
            self.sprite.rect = self.sprite.image.get_rect(center=self.end_pos)
