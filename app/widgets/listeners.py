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

    mouse_x = 0
    mouse_y = 0

    mouse_down = False

    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)
        self.scene.mouse_listeners.append(self)

        self.selected = False

    def __del__(self):
        if self in self.scene.mouse_listeners:
            self.scene.mouse_listeners.remove(self)

    def receive_mouse_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse_down(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.on_mouse_up(event)

        elif event.type == pygame.MOUSEWHEEL:
            self.on_mouse_scroll(event)

        else:
            raise ValueError(f"the given event is not a mouse event: {event}")

    # Hook method, but `super().on_mouse_down` must be called.
    def on_mouse_down(self, event):
        self.selected = self.hover

    # Hook method, but `super().on_mouse_up` must be called.
    def on_mouse_up(self, event):
        if self.hover and self.selected:
            self.on_click(event)

        self.selected = False

    # Hook method
    def on_click(self, event):
        pass

    # Hook method
    def on_mouse_scroll(self, event):
        pass

    @property
    def hover(self):
        return self.rect.global_rect.collidepoint(self.mouse_x, self.mouse_y)


class KeyboardListener(Widget, ABC):
    """
    The `KeyboardListener` class is used to broadcast a keydown event from the event loop in `app_main.py` to other
    modules of the entire program.

    When Pygame detects a keydown event, the event loop on `app_main.py` will call the `broadcast` method to broadcast
    the said event to every instance of this class.
    """

    def __init__(self, parent, *rect_args, **kwargs):
        super().__init__(parent, *rect_args, **kwargs)
        self.scene.keyboard_listeners.append(self)

    def __del__(self):
        if self in self.scene.keyboard_listeners:
            self.scene.keyboard_listeners.remove(self)

    def receive_keyboard_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event)
        elif event.type == pygame.KEYUP:
            self.key_up(event)
        else:
            raise ValueError(f"the given event is not a keyboard event: {event}")

    # Hook method
    def key_down(self, event):
        pass

    # Hook method
    def key_up(self, event):
        pass
