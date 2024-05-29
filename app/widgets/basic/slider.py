import pygame

from app.audio import play_sound
from app.shared import *
from app.widgets.listeners import MouseListener
from app.widgets.widget import Widget, WidgetComponent


class Slider(MouseListener):
    def __init__(self, parent, *rect_args,
                 min_value=0, max_value=100, default_value=0, int_only=False,
                 update_func: Callable[[int or float], None] = lambda x: None):
        super().__init__(parent, *rect_args)

        """
        Data fields
        """
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = default_value
        self.int_only = int_only

        self.set_value(default_value)

        self.update_func = update_func

        self.track_color = (100, 100, 100)
        self.thumb_color = (200, 200, 200)

        """
        Components
        """
        self.component_group = pygame.sprite.Group()

        # Measurements
        w, h = self.rect.size
        r = int(h / 3)
        d = r * 2  # Diameter = 2r

        # Track
        self.track = WidgetComponent(self, w / 2, h / 2, w - d, h / 4, "px", "tl", "ctr")
        draw_rounded_rect(self.track.image, self.track.image.get_rect(topleft=(0, 0)), self.track_color)

        # Thumb
        self.thumb = WidgetComponent(self, *self.track.rect.center, d, d, "px", "tl", "ctr")
        pygame.gfxdraw.aacircle(self.thumb.image, r, r, r, self.thumb_color)
        pygame.gfxdraw.filled_circle(self.thumb.image, r, r, r, self.thumb_color)

    def set_value(self, value, update_thumb_pos=False):
        self.current_value = int(value) if self.int_only else value

        if update_thumb_pos:
            h = self.rect.h
            m = h / 3 + h / 8
            min_x, max_x = m, self.rect.w - m

            k = (value - self.min_value) / (self.max_value - self.min_value) if self.max_value != self.min_value else 0
            x = k * (max_x - min_x) + min_x
            self.set_thumb_pos(x, False)

    def set_thumb_pos(self, x, update_value=True):
        h = self.rect.h
        m = h / 3 + h / 8

        min_x, max_x = m, self.rect.w - m
        x = max(min_x, min(max_x, x))

        if x // 25 != self.thumb.rect.centerx // 25:
            # Scroll sfx
            play_sound("assets/audio/widgets/slider.mp3")

        self.thumb.set_pos(x, h / 2, "px", "tl", "ctr")

        if update_value:
            k = (x - min_x) / (max_x - min_x)
            value = k * (self.max_value - self.min_value) + self.min_value
            self.set_value(value)

    def on_change(self):
        """
        A function that is called everytime the value is changed.
        """
        pass

    def update(self, dt):
        """"""
        super().update(dt)

        """
        Update thumb pos
        """
        if self.selected:
            self.set_thumb_pos(self.mouse_x - self.rect.global_rect.x)
            self.on_change()

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)
