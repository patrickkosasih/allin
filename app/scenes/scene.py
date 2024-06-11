import pygame
import pygame.sprite

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app_main import App
    from app.widgets.listeners import MouseListener, KeyboardListener

from app.animations.animation import AnimGroup
from app.shared import *


class Scene:
    """
    The scene class is the root container for all widgets.
    """

    def __init__(self, app: "App", scene_cache_id: str = ""):
        """
        Params:

        :param app: The main app instance.
        :param scene_cache_id: A string used to save the scene in the app's scene cache for faster loading. If set to an
                               empty string, then the scene is set to be uncacheable.
        """

        self.app = app
        self.scene_cache_id = scene_cache_id

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.anim_group = AnimGroup()

        self.mouse_listeners: list["MouseListener"] = []
        self.keyboard_listeners: list["KeyboardListener"] = []

    def update(self, dt):
        self.anim_group.update(dt)

        self.all_sprites.update(dt)
        self.all_sprites.draw(self.app.display_surface)

    def broadcast_keyboard(self, event: pygame.event.Event):
        for listener in self.keyboard_listeners:
            listener.receive_keyboard_event(event)

    def broadcast_mouse(self, event: pygame.event.Event):
        for listener in self.mouse_listeners[::-1]:
            listener.receive_mouse_event(event)

    @property
    def rect(self):
        return pygame.Rect(0, 0, *pygame.display.get_window_size())
