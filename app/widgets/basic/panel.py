import pygame

from app.scenes.scene import Scene
from app.widgets.listeners import MouseListener
from app.widgets.widget import Widget, WidgetComponent
from app.shared import *


class PanelRow(Widget):
    def __init__(self, parent: "Widget" or Scene, *rect_args):
        super().__init__(parent, *rect_args)


class Panel(MouseListener):
    DEFAULT_COLOR = (43, 193, 193)

    def __init__(self, parent: "Widget" or Scene, *rect_args,
                 base_color=DEFAULT_COLOR, base_radius=-1,
                 outer_margin=3, row_margin=1, row_height=5):
        super().__init__(parent, *rect_args)

        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        draw_rounded_rect(self.base.image, self.base.rect, color=base_color, r=base_radius)

        self.scroll_pos = 0
        self.max_scroll_pos = 0  # Probably a property
        self.scroll_vel = 0

        self.outer_margin = outer_margin
        self.row_margin = row_margin
        self.row_height = row_height

    def update(self, dt):
        pass
