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

        super().__init__(duration, int(start_val), int(end_val),
                         setter_func=lambda x: sprite.image.set_alpha(int(x)),
                         **kwargs)


class FadeSceneTransition(Animation):
    def __init__(self, duration, app: "App", scene: "Scene" or str, cache_old_scene=True, **kwargs):
        super().__init__(duration, **kwargs)

        self.app = app
        self.scene = scene
        self.cache_old_scene = cache_old_scene

        self.fader = pygame.Surface(self.app.screen.get_size())
        self.fader.fill((0, 0, 0))
        self.scene_changed = False

    def update_anim(self) -> None:
        alpha = int(self.interpolation(1 - abs(2 * self.phase - 1)) * 255)

        self.fader.set_alpha(alpha)
        self.app.screen.blit(self.fader, (0, 0))

        if self.phase >= 0.5 and not self.scene_changed:
            self.app.change_scene(self.scene, self.cache_old_scene, duration=0)
            self.scene_changed = True

    def finish(self) -> None:
        if not self.scene_changed:
            self.app.change_scene(self.scene, self.cache_old_scene, duration=0)
