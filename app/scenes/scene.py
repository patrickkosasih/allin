import pygame
import pygame.sprite

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app_main import App

from app.animations.anim_group import AnimGroup
from app.shared import *


class Scene:
    def __init__(self, app: "App"):
        self.app = app

        self.display_surface = pygame.display.get_surface()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.anim_group = AnimGroup()

    def update(self, dt):
        self.anim_group.update(dt)

        self.display_surface.fill("#123456")
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)

    @property
    def rect(self):
        return pygame.Rect(0, 0, *pygame.display.get_window_size())
