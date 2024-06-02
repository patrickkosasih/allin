import pygame

from app import app_settings
from app.shared import load_image
from app.widgets.widget import Widget


class GameBackground(Widget):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)

        show_background = app_settings.main.get_value("background")

        if show_background:
            self.image = load_image("assets/sprites/misc/background.png", size=self.rect.size)
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
