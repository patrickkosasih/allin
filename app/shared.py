import pygame
import colorsys


DEFAULT_FONT_NAME = "assets/fonts/qhyts___.ttf"
# FONT_NORMAL = pygame.font.Font(DEFAULT_FONT_NAME, 40)


def w_percent_to_px(x: float) -> float:
    return 0.01 * x * pygame.display.get_window_size()[0]


def h_percent_to_px(y: float) -> float:
    return 0.01 * y * pygame.display.get_window_size()[1]


def percent_to_px(x: float, y: float) -> tuple[float, float]:
    return w_percent_to_px(x), h_percent_to_px(y)


def hsv_factor(rgb: tuple or str, hf=0, sf=1, vf=1) -> tuple:
    """
    Takes a 24 bit RGB value and changes it according to the given HSV factors (hue, saturation, and value)

    :param rgb: The RGB value can be in tuple (e.g. (255, 255, 255)) or a string with the "#RRGGBB" format

    :param hf: Hue factor
    :param sf: Saturation factor
    :param vf: Value (brightness) factor
    """

    r, g, b = (x / 255.0 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    new_hsv = h + hf, s * sf, v * vf
    new_hsv = tuple(max(0, min(1, x)) for x in new_hsv)  # Clamp values between 0-1
    new_rgb = colorsys.hsv_to_rgb(*new_hsv)
    int_rgb = tuple(int(x * 255) for x in new_rgb)  # Convert RGB values from 0.0 - 1.0 to 0 - 255

    return int_rgb

