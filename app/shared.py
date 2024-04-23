"""
app/shared.py

A module that contains various shared functions used throughout the program.
"""

# When another module imports this module by `from app.shared import *`, all the imports below are imported as well.

import pygame.gfxdraw
from pygame.math import Vector2
from pygame.event import Event
from typing import Callable, Optional, Iterable, Generator

import colorsys
import random
import time


class FontSave:
    """
    The `FontSave` class makes creating font objects much easier by having a global font object that is shared
    throughout the program.
    """

    DEFAULT_FONT_PATH = "assets/fonts/coolvetica condensed rg.ttf"

    font_dict = {}

    @staticmethod
    def get_font(size, unit="%"):
        """
        Returns a shared font object.

        :param size: The size of the font.
        :param unit: The unit for size. Possible units: "%" - % height (default)
                                                        "px" - Pixels
        """
        if unit == "px":
            size = size / pygame.display.get_window_size()[1] * 100

        return FontSave.font_dict.setdefault(
            size,
            pygame.font.Font(FontSave.DEFAULT_FONT_PATH, int(h_percent_to_px(size)))
        )


class Layer:
    BACKGROUND = -1
    DEFAULT = 0
    TABLE = 1
    TABLE_TEXT = 2
    WINNER_CROWN = 3
    CARD = 4
    PLAYER = 5
    BLINDS_BUTTON = 6
    DEALER_BUTTON = 7
    SIDE_MENU = 8


def w_percent_to_px(x: float) -> float:
    return 0.01 * x * pygame.display.get_window_size()[0]


def h_percent_to_px(y: float) -> float:
    return 0.01 * y * pygame.display.get_window_size()[1]


def percent_to_px(x: float, y: float) -> tuple[float, float]:
    return w_percent_to_px(x), h_percent_to_px(y)


def elementwise_mult(a: Iterable, b: Iterable) -> Generator:
    return (x * y for x, y in zip(a, b))


def hsv_factor(rgb: tuple or str, hf=0, sf=1, vf=1) -> tuple:
    """
    Takes a 24 bit RGB value and changes it according to the given HSV factors (hue, saturation, and value)

    :param rgb: The RGB value can be in tuple (e.g. (255, 255, 255)) or a string with the "#RRGGBB" format

    :param hf: Hue factor
    :param sf: Saturation factor
    :param vf: Value (brightness) factor
    """
    if type(rgb) is tuple and len(rgb) == 4:
        return hsv_factor(rgb[:-1], hf, sf, vf) + (rgb[-1],)

    r, g, b = (x / 255.0 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    new_hsv = h + hf, s * sf, v * vf
    new_hsv = tuple(max(0, min(1, x)) for x in new_hsv)  # Clamp values between 0-1
    new_rgb = colorsys.hsv_to_rgb(*new_hsv)
    int_rgb = tuple(int(x * 255) for x in new_rgb)  # Convert RGB values from 0.0 - 1.0 to 0 - 255

    return int_rgb


def draw_rounded_rect(surface: pygame.Surface, rect: pygame.Rect,
                      color=(0, 0, 0), b_color=(0, 0, 0), b=0, r=-1) -> None:
    """
    Draw a rounded rectangle on the specified surface with the given rect.

    When the radius is set to a non-positive value, then the function draws a fully rounded rectangle, a.k.a. a stadium.

    A stadium is drawn by a rectangle and 2 antialiased circles. If the radius (r) is specified, the rounded rectangle
    is drawn using two stadiums and an additional horizontal rectangle.

    If the border thickness (b) is more than zero, the rounded rectangle would be drawn in two parts: the outer part
    (for the border) and the inner part (for the fill).

    :param surface: The Pygame surface to draw on
    :param rect: The rect that determines the position and dimensions rounded rectangle.

    :param color: The fill color of the button.
    :param b_color: The border color.

    :param b: The border thickness. If set to 0 then the border is not drawn.
    :param r: The corner radius of the rounded rectangle. If set to a non-positive value, then the function draws a
    fully rounded rectangle / stadium.
    """

    x, y, w, h = rect

    if len(color) == 4 and color[3] < 255:
        """
        If the color is translucent, an opaque rounded rectangle is drawn in a separate canvas, and then the alpha gets set
        after the rounded rectangle has been drawn.
        """
        canvas = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        *color, alpha = color
    else:
        canvas = surface
        alpha = 255
    
    if b > 0:
        """
        If border thickness > 0, draw two rounded rectangles (outer and inner) with b = 0.
        """
        # Outer rectangle (border)
        draw_rounded_rect(canvas, rect, b_color, b=0, r=r)

        # Inner rectangle (fill)
        inner = pygame.Surface((w, h), pygame.SRCALPHA)
        draw_rounded_rect(inner, pygame.Rect(b, b, w - 2 * b, h - 2 * b), color, b=0, r=r)
        canvas.blit(inner, rect)

    elif r == 0:
        """
        Draw a plain rectangle.
        """
        pygame.gfxdraw.box(canvas, rect, color)

    elif r < 0:
        """
        Draw a borderless stadium (fully rounded rectangle): 1 rectangle and 2 circles.
        """
        r = min(h, w) // 2

        pygame.gfxdraw.aacircle(canvas, x + r, y + r, r, color)  # Left circle
        pygame.gfxdraw.filled_circle(canvas, x + r, y + r, r, color)

        pygame.gfxdraw.aacircle(canvas, x + w - r, y + r, r, color)  # Right circle
        pygame.gfxdraw.filled_circle(canvas, x + w - r, y + r, r, color)

        pygame.gfxdraw.box(canvas, (x + r, y - 1, (w - 2 * r), h + 2), color)  # Rectangle

    else:
        """
        Draw a borderless rounded rectangle: 2 stadiums and 1 horizontal rectangle.
        """
        draw_rounded_rect(canvas, pygame.Rect(x, y, w, 2 * r), color, b=0, r=-1)  # Top rounded rectangle
        draw_rounded_rect(canvas, pygame.Rect(x, h - 2 * r, w, 2 * r), color, b=0, r=-1)  # Bottom rounded rectangle
        pygame.gfxdraw.box(canvas, (x - 1, y + r, w + 2, (h - 2 * r)), color)  # Horizontal rectangle

    if canvas is not surface:
        canvas.set_alpha(alpha)
        surface.blit(canvas, (0, 0))


def rand_color() -> tuple:
    """
    Generates a random color in an (R, G, B) tuple format.
    """
    return tuple(random.randrange(256) for _ in range(3))


def func_timer(func):
    """
    A decorator function that measures the time taken to run a function
    """
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)  # Call function
        time_taken = time.perf_counter() - time_before

        print(f"{func.__name__} took {time_taken} seconds to run")
        return ret

    return wrapper
