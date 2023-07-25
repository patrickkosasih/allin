import pygame

import rules.basic


SUIT_SPRITES = {
    "S": "assets/sprites/card/spades.png",
    "H": "assets/sprites/card/hearts.png",
    "D": "assets/sprites/card/diamonds.png",
    "C": "assets/sprites/card/clubs.png"
}


class Card(pygame.sprite.Sprite):
    global_height = 0
    scaled_card_base = None
    font = None

    def __init__(self, pos: tuple, height: float, card_data: rules.basic.Card):
        super().__init__()

        # Resize
        if height != Card.global_height:
            Card.rescale_global(height)

        self.image = Card.scaled_card_base.copy()
        self.rect = self.image.get_rect(center=pos)

        self.card_data = card_data

        self.draw_card()

    def draw_card(self):
        """
        Draw the elements of a card on the empty card base:
        1. Rank
        2. Suit icon (top left corner)
        3. Suit icon (the big one)
        """
        margin = 0.075 * self.image.get_width()

        """
        1. Rank text
        """
        rank_int = self.card_data.rank
        rank_char = rules.basic.RANK_CHARS[rank_int] if rank_int in rules.basic.RANK_CHARS else str(rank_int)
        rank_text_color = (0, 0, 0) if self.card_data.suit in ("S", "C") else (234, 61, 61)

        rank_text = Card.font.render(rank_char, True, rank_text_color)
        rank_text_rect = rank_text.get_rect(topleft=(margin, margin))
        self.image.blit(rank_text, rank_text_rect)

        """
        2. Top left corner suit
        """
        unscaled_suit = pygame.image.load(SUIT_SPRITES[self.card_data.suit])
        corner_suit_size = 0.2 * self.image.get_width()

        corner_suit = pygame.transform.smoothscale(unscaled_suit, 2 * (corner_suit_size,))
        corner_suit_rect = corner_suit.get_rect(topleft=(margin, 2.5 * margin + corner_suit_size))
        self.image.blit(corner_suit, corner_suit_rect)

        """
        3. Middle suit
        """
        big_suit_size = 0.6 * self.image.get_width()
        big_suit_pos = self.image.get_width() - margin, self.image.get_height() - margin

        big_suit = pygame.transform.smoothscale(unscaled_suit, 2 * (big_suit_size,))
        big_suit_rect = big_suit.get_rect(bottomright=big_suit_pos)
        self.image.blit(big_suit, big_suit_rect)

    @staticmethod
    def rescale_global(height):
        unscaled = pygame.image.load("assets/sprites/card/base.png")
        width = (unscaled.get_width() / unscaled.get_height()) * height

        Card.scaled_card_base = pygame.transform.smoothscale(unscaled, (width, height))
        Card.global_height = height
        Card.font = pygame.font.Font("assets/fonts/Archive-Regular.ttf", int(0.2 * height))
