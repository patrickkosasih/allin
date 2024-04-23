from typing import Type

import pygame

from app.widgets.listeners import MouseListener
from app.widgets.widget import Widget, WidgetComponent
from app.shared import *


DEFAULT_PANEL_COLOR = (24, 31, 37, 128)

SCROLL_DECELERATION_COEF = 0.25


class Panel(MouseListener):
    """
    The panel is a container for widgets that can be vertically scrolled by the user by dragging or using the mouse's
    scroll wheel.
    """

    def __init__(self, parent, *rect_args, panel_unit="%",
                 base_color=DEFAULT_PANEL_COLOR, base_radius=1, scrollable=True,
                 outer_margin=5, inner_margin=2, pack_height=10):
        super().__init__(parent, *rect_args)

        if panel_unit == "%":
            base_radius = (self.rect.h * base_radius / 100) if base_radius >= 0 else base_radius
            outer_margin = self.rect.h * outer_margin / 100
            inner_margin = self.rect.h * inner_margin / 100
            pack_height = self.rect.h * pack_height / 100

        self._outer_margin = outer_margin
        self._inner_margin = inner_margin
        self._pack_height = pack_height

        """
        Components
        """
        self._unscrolled_y_pos = {}  # Dictionary containing the original unscrolled y positions of every widget.

        self._base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        draw_rounded_rect(self._base.image, self._base.rect, color=base_color, r=base_radius)

        self._scrollable = scrollable
        self._scroll_offset = 0
        self._scroll_vel = 0

        self._next_row_y = outer_margin
        self._scroll_max = 0
        self._scroll_min = 0

        """
        Additional mouse attributes
        """
        self._prev_mouse_y = 0

    @property
    def next_pack_rect(self) -> tuple:
        """
        This property function returns 4 values for a rect (x, y, w, h) in pixels.

        The mentioned rect is used to correctly place a widget on the panel so that the widget is aligned correctly and
        neatly with uniform margins.
        """

        x = self._outer_margin
        y = self._next_row_y
        w = self.rect.w - 2 * self._outer_margin
        h = self._pack_height

        return x, y, w, h

    def add_scrollable(self, widget: Widget, repack=False):
        if repack:
            x, y, w, _ = self.next_pack_rect
            widget.rect.x = x
            widget.rect.y = y
            widget.rect.w = w

        self._unscrolled_y_pos[widget] = widget.rect.y

        self._next_row_y = max(self._next_row_y, widget.rect.bottom + self._inner_margin)
        self._scroll_min = min(self._scroll_min, self.rect.h - widget.rect.bottom - self._outer_margin)

    def on_mouse_scroll(self, event):
        if self.hover:
            self._scroll_offset += event.y * self.rect.y

    def update(self, dt):
        super().update(dt)

        """
        Scrolling mechanics
        """
        if self._scrollable:
            """
            Set scroll vel
            """
            if self.selected:  # Mouse drag
                self._scroll_vel = self.mouse_y - self._prev_mouse_y

            elif self._scroll_offset > self._scroll_max:  # Top scroll limit
                self._scroll_vel = SCROLL_DECELERATION_COEF * (self._scroll_max - self._scroll_offset)

            elif self._scroll_offset < self._scroll_min:  # Bottom scroll limit
                self._scroll_vel = SCROLL_DECELERATION_COEF * (self._scroll_min - self._scroll_offset)

            """
            Apply scroll vel
            """
            self._scroll_offset += self._scroll_vel

            """
            Slow down the scroll vel
            """
            if round(self._scroll_vel) != 0:
                self._scroll_vel -= SCROLL_DECELERATION_COEF * self._scroll_vel / abs(self._scroll_vel)
            else:
                self._scroll_vel = 0

            """
            Update the position of all scrollable widgets
            """
            for widget in self._unscrolled_y_pos:
                widget.rect.y = self._scroll_offset + self._unscrolled_y_pos[widget]

        self._prev_mouse_y = self.mouse_y
