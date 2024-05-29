import pygame
import pygame.gfxdraw

from app.animations.fade import FadeColorAnimation
from app.audio import play_sound
from app.tools.colors import hsv_factor
from app.tools.draw import draw_rounded_rect
from app.widgets.listeners import MouseListener
from app.widgets.widget import WidgetComponent


TRACK_OFF_COLOR = 60, 60, 60
TRACK_ON_COLOR = 94, 255, 97

THUMB_COLOR = 255, 255, 255, 225


class ToggleSwitch(MouseListener):
    def __init__(self, parent, *rect_args, default_state=False):
        super().__init__(parent, *rect_args)

        self._state = default_state

        self.track = WidgetComponent(self, 0, 0, 100, 100, "%", "tl", "tl")
        self.thumb = WidgetComponent(self, 0, 0, 100, 100, "%h", "ctr", "ctr")

        self._track_color = (0, 0, 0)
        self._thumb_color = (0, 0, 0)
        self.draw_track()
        self.draw_thumb()

        self.update_switch_gui(duration=0.0)

    def update_switch_gui(self, duration=0.15):
        if self._state:
            self.thumb.move_anim(duration, (0, 0), "px", "mr", "mr")
            self.draw_track(TRACK_ON_COLOR, duration)

        else:
            self.thumb.move_anim(duration, (0, 0), "px", "ml", "ml")
            self.draw_track(TRACK_OFF_COLOR, duration)

    """
    Draw / set color
    """

    def draw_track(self, color=TRACK_OFF_COLOR, duration=0.0):
        if duration > 0 and color != self._track_color:
            FadeColorAnimation(duration, self._track_color, color, setter_func=self.draw_track,
                               anim_group=self.scene.anim_group)
            return

        self._track_color = color

        draw_rounded_rect(self.track.image, self.track.rect, color)

    def draw_thumb(self, color=THUMB_COLOR):
        if color == self._track_color:
            return

        self._thumb_color = color

        r = self.thumb.rect.h // 2
        pygame.gfxdraw.aacircle(self.thumb.image, r, r, r, color)
        pygame.gfxdraw.filled_circle(self.thumb.image, r, r, r, color)

    """
    State getter and setter
    """

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: bool):
        if state != self._state:
            self._state = state
            self.update_switch_gui()

    """
    Mouse stuff
    """

    def on_click(self, event):
        if event.button == 1:
            self.state = not self.state
            play_sound(f"assets/audio/widgets/switch {'on' if self._state else 'off'}.mp3")

    def update(self, dt):
        super().update(dt)

        if self.hover:
            if self.mouse_down:
                self.draw_thumb(hsv_factor(THUMB_COLOR, vf=0.85))
            else:
                self.draw_thumb(THUMB_COLOR[:3])
        else:
            self.draw_thumb(THUMB_COLOR)
