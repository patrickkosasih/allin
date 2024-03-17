from abc import ABC, abstractmethod
from typing import Callable

import pygame
from pygame.event import Event

from app.widgets.widget import Widget


class MouseListener(Widget, ABC):
    """
    The `MouseListener` class is the super class for widgets that reacts with mouse inputs, e.g. Button, Slider, and
    Panel. Mouse states are stored in the class' attribute, and mouse events are read and handled in the update method.
    """

    all_instances: list["MouseListener"] = []
    # FIXME There is a bug where buttons can still get clicked even though they aren't shown on the screen anymore
    #  (after the scene has been changed). To fix this, move the all_instances list to the Scene class instead of being
    #  a global variable.

    mouse_x = 0
    mouse_y = 0

    mouse_down = False

    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)
        MouseListener.all_instances.append(self)

        self.selected = False

    def __del__(self):
        if self in MouseListener.all_instances:
            MouseListener.all_instances.remove(self)

    @staticmethod
    def broadcast(event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            MouseListener.mouse_down = True
            for listener in MouseListener.all_instances:
                listener.on_mouse_down(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            MouseListener.mouse_down = False
            for listener in MouseListener.all_instances:
                listener.on_mouse_up(event)

        elif event.type == pygame.MOUSEWHEEL:
            for listener in MouseListener.all_instances:
                listener.on_mouse_scroll(event)

    def on_mouse_down(self, event):
        self.selected = self.hover

    def on_mouse_up(self, event):
        if self.hover and self.selected:
            self.on_click(event)

        self.selected = False

    def on_click(self, event):
        pass

    def on_mouse_scroll(self, event):
        pass

    @property
    def hover(self):
        return self.rect.global_rect.collidepoint(self.mouse_x, self.mouse_y)


class KeyboardListener(ABC):
    """
    The `KeyboardListener` class is used to broadcast a keydown event from the event loop in `app_main.py` to other
    modules of the entire program.

    When Pygame detects a keydown event, the event loop on `app_main.py` will call the `broadcast` method to broadcast
    the said event to every instance of this class.
    """

    all_instances: list["KeyboardListener"] = []
    # FIXME The all instances list should be a Scene attribute instead of a global variable (same as MouseListener).

    @staticmethod
    def broadcast(event):
        """
        This method is called by the event loop in `app_main.py`.
        """
        for listener in KeyboardListener.all_instances:
            listener.key_down(event)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        KeyboardListener.all_instances.append(self)

    def __del__(self):
        if self in KeyboardListener.all_instances:
            KeyboardListener.all_instances.remove(self)

    @abstractmethod
    def key_down(self, event):
        pass
