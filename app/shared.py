import pygame
import pygame.gfxdraw
import colorsys
import random


class FontSave:
    DEFAULT_FONT_PATH = "assets/fonts/coolvetica condensed rg.ttf"

    font_dict = {}

    @staticmethod
    def get_font(percent_size):
        """
        Returns a shared font object.

        :param percent_size: The size of the font. Unit: % window height
        """
        return FontSave.font_dict.setdefault(
            percent_size,
            pygame.font.Font(FontSave.DEFAULT_FONT_PATH, int(h_percent_to_px(percent_size)))
        )


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


def draw_rounded_rect(surface: pygame.Surface, rect: pygame.Rect,
                      color=(0, 0, 0), b_color=(0, 0, 0), b=0) -> None:
    """
    Draw a bordered rounded rectangle with the height as its radius.

    A complete rounded rectangle consists of the outer part (for the border) and the inner part (for the fill).
    A rounded rectangle is drawn by a rectangle and two circles, complete with anti aliasing.

    :param surface: The Pygame surface to draw on
    :param rect: The rect that determines the position and dimensions rounded rectangle.

    :param color: The fill color of the button.
    :param b_color: The border color.
    :param b: The border thickness. If set to 0 then the border is not drawn.
    """

    x, y, w, h = rect
    r = h // 2
    
    if b > 0:
        """
        If border thickness > 0, draw two rounded rectangles (outer and inner) with b = 0.
        """
        # Outer rectangle (border)
        draw_rounded_rect(surface, rect, b_color, b=0)

        # Inner rectangle (fill)
        inner = pygame.Surface((w, h), pygame.SRCALPHA)
        draw_rounded_rect(inner, pygame.Rect(b, b, w - 2 * b, h - 2 * b), color, b=0)
        surface.blit(inner, rect)

    else:
        """
        Draw a borderless rounded rectangle
        """
        pygame.gfxdraw.aacircle(surface, x + r, y + r, r, color)  # Left circle
        pygame.gfxdraw.filled_circle(surface, x + r, y + r, r, color)

        pygame.gfxdraw.aacircle(surface, x + w - r, y + r, r, color)  # Right circle
        pygame.gfxdraw.filled_circle(surface, x + w - r, y + r, r, color)

        pygame.gfxdraw.box(surface, (x + r, y - 1, (w - 2 * r), h + 2), color)  # Rectangle


def rand_color() -> tuple:
    """
    Generates a random color in an (R, G, B) tuple format.
    """
    return tuple(random.randrange(256) for _ in range(3))
