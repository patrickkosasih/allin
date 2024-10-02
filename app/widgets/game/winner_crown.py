import pygame

from app.animations.animation import AnimGroup
from app.animations.move import MoveAnimation
from app.animations.var_slider import VarSlider
from app.tools import app_timer
from app.widgets.game.player_display import PlayerDisplay
from app.shared import *
from app.widgets.widget import Widget, WidgetComponent

DIMENSIONS_MULT = (1.2, 2.5)

MAIN_COLOR = 255, 226, 148
SIDE_COLOR = 222, 222, 222


def generate_pot_text(pots_won: list[int]) -> str:
    first_won, last_won = min(pots_won), max(pots_won)

    if first_won == last_won:
        if first_won == 0:
            return "Main pot"
        else:
            return f"Side pot {first_won}"

    else:
        if first_won == 0:
            if last_won == 1:
                return "Main pot + Side pot 1"
            else:
                return f"Main pot + Side pots 1-{last_won}"

        else:
            return f"Side pots {first_won}-{last_won}"


class WinnerCrown(Widget):
    """
    The winner crown is a widget placed behind a player display for the player who has won the hand. A winner crown is
    not part of the player display, but is placed based on the player display's position.

    A winner crown widget has 5 components:
    1. Highlight        : A bright border around the player display.
    2. Crown            : A crown icon placed above the player's profile icon.
    3. Main text        : A text saying "Winner!" or "Side Pot Winner!"
    4. Sub text         : A smaller text that shows the amount of chips won and which pots were won by the player.
    5. Text shadow      : A subtle dark background behind the texts to make them more readable.
    """

    def __init__(self, parent, player: PlayerDisplay, show_pots: bool = False):
        dimensions = elementwise_mult(player.rect.size, DIMENSIONS_MULT)

        super().__init__(parent, *player.rect.center, *dimensions, "px", "tl", "ctr")
        self.layer = Layer.WINNER_CROWN

        self.player: PlayerDisplay = player
        self.show_pots: bool = show_pots

        self.is_main_winner: bool = 0 in self.player.player_data.player_hand.pots_won

        self.color = MAIN_COLOR if self.is_main_winner else SIDE_COLOR

        """
        Components
        
        The components are initialized on the `init_components` method where it still uses the oldschool way of manually
        calculating pixel measurements for most parts.
        """
        self.highlight = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")
        self.crown = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")

        self.text_shadow = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")  # Layered under the texts
        self.text = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")
        self.sub_text = WidgetComponent(self, 0, 0, 0, 0, "px", "tl", "ctr")

        """
        Hidden positions: Positions to go to when the winner crown is reset.
        """
        self.crown_hidden_pos = None
        self.text_hidden_pos = None

        self.init_components()

    def init_components(self):
        """
        Initialize the components of a winner crown and animate them:
        1. Highlight
        2. Crown
        3. Main text
        4. Sub text
        5. Text shadow
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
        draw_rounded_rect(self.highlight.image, pygame.Rect(0, 0, *highlight_dimensions), self.color)

        self.highlight.fade_anim(2.5, 0)

        """
        2. Crown
        """
        self.crown_hidden_pos = Vector2(pfp_rect.center) + d_pos
        crown_shown_pos = self.crown_hidden_pos - Vector2(percent_to_px(0, 7.5))

        if self.is_main_winner:
            self.crown.image = load_image("assets/sprites/winner crown/main winner.png", 2 * (w_percent_to_px(3),))
        else:
            self.crown.image = load_image("assets/sprites/winner crown/side winner.png", 2 * (w_percent_to_px(3),))

        self.crown.set_pos(*self.crown_hidden_pos, "px", "tl", "ctr")

        self.crown.move_anim(0.5, crown_shown_pos)

        """
        3. Main text
        """
        self.text_hidden_pos = Vector2(head_base_rect.center) + d_pos
        text_shown_pos = self.text_hidden_pos + Vector2(percent_to_px(0, 10.5))
        winner_text_str = "Winner!" if self.is_main_winner else "Side Pot Winner!"

        if self.player.sub_text_str == "":
            text_shown_pos -= Vector2(0, self.player.sub_base.rect.h)

        self.text.image = FontSave.get_font(4).render(winner_text_str, True, self.color)
        self.text.set_pos(*self.text_hidden_pos, "px", "tl", "ctr")

        self.text.move_anim(0.75, text_shown_pos)

        """
        4. Sub text
        """
        sub_text_shown_pos = text_shown_pos + Vector2(0, self.text.rect.h * 0.35)
        self.set_sub_text(show_pots=self.show_pots)

        self.sub_text.set_pos(*self.text_hidden_pos, "px", "tl", "ctr")
        self.sub_text.move_anim(0.75, sub_text_shown_pos, "px", "tl", "mt")

        """
        5. Text shadow
        """
        self.text_shadow.image = load_image("assets/sprites/winner crown/text shadow.png", highlight_dimensions)
        self.text_shadow.set_pos(*sub_text_shown_pos, "px", "tl", "ctr")

        self.text_shadow.image.set_alpha(0)
        self.text_shadow.fade_anim(0.75, 169)

    def set_sub_text(self, show_pots=False):
        """
        Set the sub text to show either the player's winnings last round, or which pots the player has won. If the
        argument is set to show the pots, the text changes again by itself to the player's winnings after a few seconds.

        :param show_pots: True: Show the pots won, and then the winnings.
                          False: Show the winnings.
        """
        if show_pots:
            sub_text_str = generate_pot_text(self.player.player_data.player_hand.pots_won)

            app_timer.Sequence([
                3,
                lambda: self.sub_text.fade_anim(0.25, 0),
                0.25,
                lambda: self.set_sub_text(False),
                lambda: self.sub_text.fade_anim(0.25, 255),
            ])

        else:
            sub_text_str = f"+${self.player.player_data.player_hand.winnings:,}"

        self.sub_text.image = FontSave.get_font(3).render(sub_text_str, True, self.color)


    def hide(self):
        """
        Move the crown and winner text back to its hidden positions behind the player display.
        """
        self.crown.move_anim(0.5, self.crown_hidden_pos)
        self.text.move_anim(0.75, self.text_hidden_pos)
        self.sub_text.move_anim(0.85, self.text_hidden_pos)
        self.text_shadow.fade_anim(0.75, 0)
