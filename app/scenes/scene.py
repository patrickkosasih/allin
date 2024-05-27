import pygame
import pygame.sprite

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app_main import App
    from app.widgets.listeners import MouseListener, KeyboardListener

from app.animations.animation import AnimGroup
from app.shared import *


class Scene:
    def __init__(self, app: "App", scene_id: str):
        self.app = app
        self.scene_id = scene_id
        self.bg_color = "#123456"

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.anim_group = AnimGroup()

        self.mouse_listeners: list["MouseListener"] = []
        self.keyboard_listeners: list["KeyboardListener"] = []

    def update(self, dt):
        self.anim_group.update(dt)

        self.app.display_surface.fill(self.bg_color)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.app.display_surface)

    def broadcast_keyboard(self, event: pygame.event.Event):
        for listener in self.keyboard_listeners:
            listener.receive_keyboard_event(event)

    def broadcast_mouse(self, event: pygame.event.Event):
        for listener in self.mouse_listeners:
            listener.receive_mouse_event(event)

    @property
    def rect(self):
        return pygame.Rect(0, 0, *pygame.display.get_window_size())
