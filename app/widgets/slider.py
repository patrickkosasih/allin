from typing import Callable

import pygame
from app.shared import *


class Slider(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions,
                 min_value=0, max_value=100, default_value=0, int_only=False,
                 update_func: Callable[[int or float], None] = lambda x: None):
        super().__init__()

        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.global_rect = self.rect.copy()

        """
        Data fields
        """
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = default_value
        self.int_only = int_only

        self.set_value(default_value)

        self.update_func = update_func

        self.track_color = (100, 100, 100)
        self.thumb_color = (200, 200, 200)

        """
        Mouse data fields
        """
        self.prev_mouse_down = False
        self.selected = False

        """
        Components
        """
        self.component_group = pygame.sprite.Group()

        # Measurements
        w, h = dimensions
        r = int(h / 3)
        d = r * 2  # Diameter = 2r

        # Track
        self.track = pygame.sprite.Sprite(self.component_group)

        self.track.image = pygame.Surface((w - d, h / 4), pygame.SRCALPHA)
        self.track.rect = self.track.image.get_rect(center=(w / 2, h / 2))
        draw_rounded_rect(self.track.image, self.track.image.get_rect(topleft=(0, 0)), self.track_color)

        # Thumb
        self.thumb = pygame.sprite.Sprite(self.component_group)

        self.thumb.image = pygame.Surface((d, d), pygame.SRCALPHA)
        self.thumb.rect = self.thumb.image.get_rect(center=self.track.rect.center)
        pygame.gfxdraw.aacircle(self.thumb.image, r, r, r, self.thumb_color)
        pygame.gfxdraw.filled_circle(self.thumb.image, r, r, r, self.thumb_color)

    def set_value(self, value, update_thumb_pos=False):
        self.current_value = int(value) if self.int_only else value

        if update_thumb_pos:
            h = self.rect.h
            m = h / 3 + h / 8
            min_x, max_x = m, self.rect.w - m

            k = (value - self.min_value) / (self.max_value - self.min_value)
            x = k * (max_x - min_x) + min_x
            self.set_thumb_pos(x - self.global_rect.x, False)

    def set_thumb_pos(self, x, update_value=True):
        h = self.rect.h
        m = h / 3 + h / 8

        min_x, max_x = m, self.rect.w - m
        x = max(min_x, min(max_x, x))

        self.thumb.rect = self.thumb.image.get_rect(center=(x, h / 2))

        if update_value:
            k = (x - min_x) / (max_x - min_x)
            value = k * (self.max_value - self.min_value) + self.min_value
            self.set_value(value)

    def set_color(self):
        pass

    def on_change(self):
        """
        A function that is called everytime the value is changed.
        """
        pass

    def update(self, dt):
        """"""

        """
        Update mouse states
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hover = self.global_rect.collidepoint(mouse_x, mouse_y)
        mouse_down = pygame.mouse.get_pressed()[0]  # Left mouse button

        if hover and mouse_down and self.prev_mouse_down != mouse_down:
            self.selected = True
        elif not mouse_down:
            self.selected = False

        self.prev_mouse_down = mouse_down

        """
        Update thumb pos
        """
        if self.selected:
            self.set_thumb_pos(mouse_x - self.rect.left - self.global_rect.x)
            self.on_change()

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)
