import pygame.sprite

from app.animations.var_slider import VarSlider


class FadeAlpha(VarSlider):
    def __init__(self, duration, sprite: pygame.sprite.Sprite,
                 start_val: int or float, end_val: int or float, **kwargs):

        if start_val not in range(256) or end_val not in range(256):
            raise ValueError("start and end val must be between 0-255")

        super().__init__(duration, int(start_val), int(end_val),
                         setter_func=lambda x: sprite.image.set_alpha(int(x)),
                         **kwargs)
