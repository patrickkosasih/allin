import pygame.sprite
from pygame.math import Vector2

from app.animations.animation import Animation
from app.animations.interpolations import *


class MoveAnimation(Animation):
    def __init__(self, duration, sprite: pygame.sprite.Sprite,
                 start_pos: tuple or Vector2 or None, end_pos: tuple or Vector2,
                 **kwargs):
        super().__init__(duration, **kwargs)

        self.sprite = sprite
        self.start_pos = Vector2(start_pos) if start_pos else Vector2(self.sprite.rect.center)
        self.end_pos = Vector2(end_pos)

    def update_anim(self):
        current_pos = self.start_pos + self.interpol_phase * (self.end_pos - self.start_pos)

        self.sprite.rect = self.sprite.image.get_rect(center=current_pos)

    def finish(self):
        self.sprite.rect = self.sprite.image.get_rect(center=self.end_pos)
