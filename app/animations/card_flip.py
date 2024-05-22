# Type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.widgets.game.card import Card

import pygame.transform
from app.animations.animation import Animation


class CardFlipAnimation(Animation):
    """
    The card flip animation class animates card flips/reveals by scaling the unscaled card sprite horizontally.
    """

    def __init__(self, duration: float, card: "Card",
                 **kwargs):
        super().__init__(duration, **kwargs)

        self.card = card

        self.unscaled_image = card.image.copy()

        self.center = card.rect.center
        self.original_width = card.image.get_width()
        self.original_height = card.image.get_height()

    def update_anim(self) -> None:
        w = abs(1 - 2 * self.interpol_phase) * self.original_width
        h = self.original_height

        if self.interpol_phase >= 0.5 and not self.card.is_revealed:
            self.card.draw_card_front()
            self.unscaled_image = self.card.card_front
            self.card.is_revealed = True

        self.card.image = pygame.transform.smoothscale(self.unscaled_image, (w, h))
        self.card.rect = self.card.image.get_rect(center=self.center)


    def finish(self) -> None:
        if not self.card.is_revealed:
            self.card.draw_card_front()

        self.card.image = self.card.card_front.copy()
