import pygame

from app.scenes.scene import Scene
from app.widgets.widget import Widget


class Panel(Widget):
    def __init__(self, parent: "Widget" or Scene, *rect_args):
        super().__init__(parent, *rect_args)
