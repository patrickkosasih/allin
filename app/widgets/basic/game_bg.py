import pygame

from app import app_settings
from app.shared import load_image
from app.widgets.widget import Widget


class GameBackground(Widget):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)

        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/sprites/misc/background.png"), self.rect.size
        ).convert()
