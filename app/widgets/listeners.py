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

    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)

        self.mouse_x = 0
        self.mouse_y = 0

        self.hover = False
        self.mouse_down = False
        self.prev_mouse_down = False

        self.click = False
        self.selected = False

    def update(self, dt):
        """"""

        """
        Updated every tick
        """
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        self.hover = self.rect.global_rect.collidepoint(self.mouse_x, self.mouse_y)
        self.mouse_down = pygame.mouse.get_pressed()[0]  # Left mouse button

        """
        Mouse up -> Mouse down
        """
        if self.mouse_down and not self.prev_mouse_down:
            self.selected = self.hover

        """
        Mouse down -> Mouse up
        """
        if self.prev_mouse_down and not self.mouse_down:
            self.click = self.hover and self.selected
            self.selected = False
        else:
            self.click = False

        self.prev_mouse_down = self.mouse_down


class KeyboardListener(ABC):
    """
    The `KeyboardListener` class is used to broadcast a keydown event from the event loop in `app_main.py` to other
    modules of the entire program.

    When Pygame detects a keydown event, the event loop on `app_main.py` will call the `broadcast` method to broadcast
    the said event to every instance of this class.
    """

    all_instances: list["KeyboardListener"] = []

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
        KeyboardListener.all_instances.remove(self)

    @abstractmethod
    def key_down(self, event):
        pass
