import pygame

from app.animations.anim_group import AnimGroup
from app.animations.move import MoveAnimation
from app.animations.var_slider import VarSlider
from app.widgets.game.player_display import ComponentCodes, PlayerDisplay
from app.shared import *


DIMENSIONS_MULT = (1.2, 1.9)

TEXT_COLOR = 255, 226, 148


class WinnerCrown(pygame.sprite.Sprite):
    """
    The winner crown is a widget placed behind a player display for the player who has won the deal. A winner crown is
    not part of the player display, but is placed based on the player display's position.

    A winner crown widget has 3 components:
    1. Highlight
    2. Crown
    3. "Winner!" text
    """

    def __init__(self, player: PlayerDisplay):
        super().__init__()

        dimensions = player.rect.width * DIMENSIONS_MULT[0], player.rect.height * DIMENSIONS_MULT[1]

        """
        Sprite attributes
        """
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.layer = Layer.WINNER_CROWN

        """
        Misc
        """
        self.player = player
        self.anim_group = AnimGroup()

        """
        Components
        """
        self.component_group = pygame.sprite.Group()
        self.highlight = pygame.sprite.Sprite()
        self.crown = pygame.sprite.Sprite()
        self.text = pygame.sprite.Sprite()

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

        head_base_rect = self.player.components[ComponentCodes.HEAD_BASE].rect
        pfp_rect = self.player.components[ComponentCodes.PROFILE_PIC].rect

        """
        1. Highlight
        """
        highlight_pos = Vector2(head_base_rect.center) + d_pos
        highlight_dimensions = Vector2(head_base_rect.width, head_base_rect.height)

        th = w_percent_to_px(2)  # Thickness of highlight
        highlight_dimensions += Vector2(th, th)

        self.highlight.image = pygame.Surface(highlight_dimensions, pygame.SRCALPHA)
        self.highlight.rect = self.highlight.image.get_rect(center=highlight_pos)
        draw_rounded_rect(self.highlight.image, pygame.Rect(0, 0, *highlight_dimensions), TEXT_COLOR)
        self.component_group.add(self.highlight)

        highlight_anim = VarSlider(2.5, 255, 0, setter_func=self.set_highlight_alpha)
        self.anim_group.add(highlight_anim)

        """
        2. Crown
        """
        self.crown_hidden_pos = Vector2(pfp_rect.center) + d_pos
        crown_pos = self.crown_hidden_pos - Vector2(percent_to_px(0, 7.5))

        self.crown.image = pygame.transform.smoothscale(pygame.image.load("assets/sprites/misc/crown.png"),
                                                        2 * (w_percent_to_px(3),))
        self.crown.rect = self.crown.image.get_rect(center=self.crown_hidden_pos)
        self.component_group.add(self.crown)

        crown_anim = MoveAnimation(0.5, self.crown, self.crown_hidden_pos, crown_pos)
        self.anim_group.add(crown_anim)

        """
        3. Winner text
        """
        self.text_hidden_pos = Vector2(head_base_rect.center) + d_pos
        text_pos = self.text_hidden_pos + Vector2(percent_to_px(0, 10.5))

        self.text.image = FontSave.get_font(4).render("Winner!", True, TEXT_COLOR)
        self.text.rect = self.text.image.get_rect(midbottom=self.text_hidden_pos)
        self.component_group.add(self.text)

        text_anim = MoveAnimation(0.75, self.text, self.text_hidden_pos, text_pos)
        self.anim_group.add(text_anim)

    def set_highlight_alpha(self, alpha):
        self.highlight.image.set_alpha(int(alpha))

    def hide(self):
        """
        Move the crown and winner text back to its hidden positions behind the player display.
        """

        crown_anim = MoveAnimation(0.5, self.crown, None, self.crown_hidden_pos)
        self.anim_group.add(crown_anim)

        text_anim = MoveAnimation(0.75, self.text, None, self.text_hidden_pos)
        self.anim_group.add(text_anim)

    def update(self, dt):
        self.anim_group.update(dt)
        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)
