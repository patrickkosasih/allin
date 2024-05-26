import pygame.sprite

from app.animations.animation import Animation
from app.animations.var_slider import VarSlider

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app_main import App
    from app.scenes.scene import Scene


class FadeAlphaAnimation(VarSlider):
    def __init__(self, duration, sprite: pygame.sprite.Sprite,
                 start_val: int or float, end_val: int or float, **kwargs):

        if start_val == -1:
            start_val = sprite.image.get_alpha()

        if start_val not in range(256) or end_val not in range(256):
            raise ValueError("start and end val must be between 0-255")

        super().__init__(duration, start_val, end_val,
                         setter_func=lambda x: sprite.image.set_alpha(int(x)),
                         **kwargs)


class FadeSceneAnimation(VarSlider):
    def __init__(self, duration, app: "App",
                 start_val: int or float, end_val: int or float, **kwargs):

        super().__init__(duration, start_val, end_val,
                         setter_func=self.set_fader_alpha,
                         **kwargs)

        if start_val not in range(256) or end_val not in range(256):
            raise ValueError("start and end val must be between 0-255")

        self.app = app

        self.fader = pygame.Surface(self.app.screen.get_size())
        self.fader.fill((0, 0, 0))

    def set_fader_alpha(self, alpha) -> None:
        self.fader.set_alpha(int(alpha))
        self.app.screen.blit(self.fader, (0, 0))
