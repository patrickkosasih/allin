import pygame

from app.animations.animation import AnimGroup
from app.animations.move import MoveAnimation
from app.animations.var_slider import VarSlider
from app.widgets.game.player_display import ComponentCodes, PlayerDisplay
from app.shared import *
from app.widgets.widget import Widget, WidgetComponent

DIMENSIONS_MULT = (1.2, 1.9)

TEXT_COLOR = 255, 226, 148


class WinnerCrown(Widget):
    """
    The winner crown is a widget placed behind a player display for the player who has won the deal. A winner crown is
    not part of the player display, but is placed based on the player display's position.

    A winner crown widget has 3 components:
    1. Highlight
    2. Crown
    3. "Winner!" text
    """

    def __init__(self, parent, player: PlayerDisplay):
        dimensions = elementwise_mult(player.rect.size, DIMENSIONS_MULT)

        super().__init__(parent, *player.rect.center, *dimensions, "px", "tl", "ctr")
        self.layer = Layer.WINNER_CROWN

        self.player: PlayerDisplay = player

        """
        Components
        """
        self.highlight = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")
        self.crown = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")
        self.text = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")

        """
        Hidden positions: Positions to go to when the winner crown is reset.
        """
        self.crown_hidden_pos = None
        self.text_hidden_pos = None

        self.init_components()

    def init_components(self):
        """
        Initialize the components of a winner crown along with its starting animations:
        1. Highlight
        2. Crown
        3. "Winner!" text
        """

        d_pos = Vector2(self.player.rect.topleft) - Vector2(self.rect.topleft)
        """The difference of the top left corner coordinates between the winner crown widget and the player display."""

        head_base_rect = self.player.head_base.rect
        pfp_rect = self.player.profile_pic.rect

        """
        1. Highlight
        """
        th = w_percent_to_px(2)  # Thickness of highlight
        highlight_pos = Vector2(head_base_rect.center) + d_pos
        highlight_dimensions = Vector2(head_base_rect.width, head_base_rect.height) + Vector2(th, th)

        self.highlight.image = pygame.Surface(highlight_dimensions, pygame.SRCALPHA)
        self.highlight.set_pos(*highlight_pos, "px", "tl", "ctr")
        draw_rounded_rect(self.highlight.image, pygame.Rect(0, 0, *highlight_dimensions), TEXT_COLOR)

        self.highlight.fade_anim(2.5, 0)

        """
        2. Crown
        """
        self.crown_hidden_pos = Vector2(pfp_rect.center) + d_pos
        crown_shown = self.crown_hidden_pos - Vector2(percent_to_px(0, 7.5))

        self.crown.image = load_image("assets/sprites/misc/crown.png", 2 * (w_percent_to_px(3),))
        self.crown.set_pos(*self.crown_hidden_pos, "px", "tl", "ctr")

        self.crown.move_anim(0.5, crown_shown)

        """
        3. Winner text
        """
        self.text_hidden_pos = Vector2(head_base_rect.center) + d_pos
        text_shown_pos = self.text_hidden_pos + Vector2(percent_to_px(0, 10.5))

        self.text.image = FontSave.get_font(4).render("Winner!", True, TEXT_COLOR)
        self.text.set_pos(*self.text_hidden_pos, "px", "tl", "ctr")

        self.text.move_anim(0.75, text_shown_pos)

    def hide(self):
        """
        Move the crown and winner text back to its hidden positions behind the player display.
        """
        self.crown.move_anim(0.5, self.crown_hidden_pos)
        self.text.move_anim(0.75, self.text_hidden_pos)
