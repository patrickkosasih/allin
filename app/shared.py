"""
app/shared.py

A module that contains various shared functions used throughout the program.
"""
import os

# When another module imports this module by `from app.shared import *`, all the imports below are imported as well.

import pygame
from pygame.math import Vector2
from pygame.event import Event
from typing import Callable, Optional, Iterable, Generator
import time

from app.tools.colors import hsv_factor, rand_color
from app.tools.draw import draw_rounded_rect


SAVE_FOLDER_PATH = os.path.join(os.getenv("localappdata"), "Allin")

if not os.path.isdir(SAVE_FOLDER_PATH):
    os.mkdir(SAVE_FOLDER_PATH)


"""
Image loading-related tools
"""
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

    @staticmethod
    def reset():
        FontSave.font_dict = {}


def load_image(path: str,
               size: None or tuple = None,
               convert = True) -> pygame.Surface:
    """
    Load an image file into a pygame.Surface object, and convert it to the correct pixel format using `convert_alpha`.

    A much simpler way of writing `pygame.image.load(path).convert_alpha()`.

    :param path: Path to the image file.
    :param size: If not set to None then the image is resized to the given size.
    :param convert: Convert the image using `convert_alpha` or not
    :return: The loaded and converted image.
    """
    image = pygame.image.load(path)

    if size:
        image = pygame.transform.smoothscale(image, size)
    if convert:
        image = image.convert_alpha()

    return image


"""
Universal layer order constants
"""
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


"""
% to px conversion functions
"""
def w_percent_to_px(x: float) -> float:
    return 0.01 * x * pygame.display.get_window_size()[0]


def h_percent_to_px(y: float) -> float:
    return 0.01 * y * pygame.display.get_window_size()[1]


def percent_to_px(x: float, y: float) -> tuple[float, float]:
    return w_percent_to_px(x), h_percent_to_px(y)


def elementwise_mult(a: Iterable, b: Iterable) -> Generator:
    return (x * y for x, y in zip(a, b))


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
