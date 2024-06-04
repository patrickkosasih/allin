from app import app_settings
from app.animations.interpolations import ease_out
from app.scenes.scene import Scene
from app.shared import Layer, func_timer
from app.widgets.basic.fps_counter import FPSCounter
from app.widgets.basic.game_bg import GameBackground
from app.widgets.widget import Widget


class OverlayScene(Scene):
    def __init__(self, app):
        super().__init__(app, "")

        self.fader = Widget(self, 0, 0, 100, 100, "%", "tl", "tl")
        self.fader.image.fill((0, 0, 0))
        self.fader.image.set_alpha(0)

        self.fps_counter = FPSCounter(self, 0.5, 0.5, 15, 5, "%", "tl", "tl")


class BackgroundScene(Scene):
    def __init__(self, app):
        super().__init__(app, "")

        self.background = GameBackground(self, 0, 0, 101, 101, "%w", "ctr", "ctr")

    def move_on_startup(self):
        if not app_settings.main.get_value("background"):
            return

        self.app.background_scene.background.set_pos(0, -100, "%", "mb", "mb")
        self.app.background_scene.background.move_anim(3, (0, 0), "px", "ctr", "ctr",
                                                       interpolation=lambda x: ease_out(x, power=2.5))
        self.app.background_scene.background.fade_anim(4, 254)
        # Setting the background's alpha to 255 drops the FPS a lot, but setting it anywhere below 255 doesn't, for some
        # weird reason.

    def update(self, dt):
        super().update(dt)
