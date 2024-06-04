import pygame.sprite

from app.animations.animation import Animation
from app.animations.var_slider import VarSlider

from typing import TYPE_CHECKING, Callable

from app.tools.colors import mix_color

if TYPE_CHECKING:
    from app.app_main import App
    from app.scenes.scene import Scene


class FadeAlphaAnimation(VarSlider):
    def __init__(self, duration, sprite: pygame.sprite.Sprite,
                 start_val: int or float, end_val: int or float, **kwargs):

        if start_val == -1:
            start_val = sprite.image.get_alpha()
            if start_val is None:
                start_val = 255

        if start_val not in range(256) or end_val not in range(256):
            raise ValueError("start and end val must be between 0-255")

        super().__init__(duration, start_val, end_val,
                         setter_func=lambda x: sprite.image.set_alpha(int(x)),
                         **kwargs)


class FadeColorAnimation(Animation):
    def __init__(self, duration, start_color: tuple, end_color: tuple,
                 setter_func: Callable[[tuple], None] = lambda x: None,
                 **kwargs):

        self.start_color = start_color
        self.end_color = end_color

        self.setter_func = setter_func

        super().__init__(duration, **kwargs)

    def update_anim(self) -> None:
        self.setter_func(mix_color(self.start_color, self.end_color, self.interpol_phase))

    def finish(self) -> None:
        self.setter_func(self.end_color)

