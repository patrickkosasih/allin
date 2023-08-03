import pygame
from pygame.math import Vector2

from app.widgets.player_display import ComponentCodes, PlayerDisplay
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

        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.layer = Layer.WINNER_CROWN

        self.player = player

        self.component_group = pygame.sprite.Group()
        self.highlight = pygame.sprite.Sprite()
        self.crown = pygame.sprite.Sprite()
        self.text = pygame.sprite.Sprite()

        self.init_components()

    def init_components(self):
        """

        :return:
        """
        d_pos = Vector2(self.player.rect.topleft) - Vector2(self.rect.topleft)
        """The difference of the top left corner coordinates between the winner crown widget and the player display."""

        """
        1. Highlight
        """
        head_base_rect = self.player.components[ComponentCodes.HEAD_BASE].rect
        highlight_pos = Vector2(head_base_rect.center) + d_pos

        highlight_dimensions = Vector2(head_base_rect.width, head_base_rect.height)
        th = w_percent_to_px(2)  # Thickness of highlight
        highlight_dimensions = highlight_dimensions + Vector2(th, th)

        self.highlight.image = pygame.Surface(highlight_dimensions, pygame.SRCALPHA)
        self.highlight.rect = self.highlight.image.get_rect(center=highlight_pos)

        draw_rounded_rect(self.highlight.image, pygame.Rect(0, 0, *highlight_dimensions), TEXT_COLOR)

        self.component_group.add(self.highlight)

        """
        2. Crown
        """
        m = Vector2(0, - w_percent_to_px(1))
        crown_pos = Vector2(self.player.components[ComponentCodes.PROFILE_PIC].rect.midtop) + d_pos

        self.crown.image = pygame.transform.smoothscale(pygame.image.load("assets/sprites/crown.png"),
                                                        2 * (w_percent_to_px(3),))
        self.crown.rect = self.crown.image.get_rect(midbottom=crown_pos)
        self.component_group.add(self.crown)


        """
        3. Winner text
        """
        text_pos = Vector2(self.player.components[ComponentCodes.SUB_BASE].rect.midbottom) + d_pos

        self.text.image = FontSave.get_font(4).render("Winner!", True, TEXT_COLOR)
        self.text.rect = self.text.image.get_rect(midtop=text_pos)

        self.component_group.add(self.text)

    def update(self, dt):
        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)
