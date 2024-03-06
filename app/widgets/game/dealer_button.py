import pygame

from app.shared import Layer, h_percent_to_px
from app.widgets.widget import Widget

SPRITE_PATHS = {
    "D": "assets/sprites/dealer buttons/d.png",
    "SB": "assets/sprites/dealer buttons/sb.png",
    "BB": "assets/sprites/dealer buttons/bb.png"
}


class DealerButton(Widget):
    def __init__(self, parent, x, y, button_type="D", d_percent=3.5, **kwargs):
        """
        Parameters:

        :param pos: Initial (x, y) position. Units are in pixels, anchor is on the top left, and pivot is the center.
        :param button_type: The type of the button, or the letter(s) that are shown on the button.
                            Possible types: "D", "SB", "BB". Case-insensitive.
        :param d_percent: The diameter of the button. Units are in percent of the screen's height.
        :param kwargs: Keyword arguments for the Widget superclass.
        """

        d_px = h_percent_to_px(d_percent)

        super().__init__(parent, x, y, d_px, d_px, "px", "tl", "ctr")

        button_type = button_type.upper()
        if button_type not in SPRITE_PATHS:
            raise ValueError(f"invalid button type: {button_type}")

        self._image = pygame.transform.smoothscale(pygame.image.load(SPRITE_PATHS[button_type]), self.rect.size)
        self.layer = Layer.DEALER_BUTTON if button_type == "D" else Layer.BLINDS_BUTTON
