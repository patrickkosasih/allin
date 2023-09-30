import pygame

import rules.basic
from app.animations.anim_group import AnimGroup
from app.shared import Layer
from app.animations.card_flip import CardFlipAnimation

SUIT_SPRITE_PATHS = {
    "S": "assets/sprites/card/spades.png",
    "H": "assets/sprites/card/hearts.png",
    "D": "assets/sprites/card/diamonds.png",
    "C": "assets/sprites/card/clubs.png"
}


class Card(pygame.sprite.Sprite):
    """
    The card sprite represents a single card, whether it's a pocket card or a community card.

    The `Card` class has some global attributes, which means some properties of a card share the same global variable.
    """

    global_height = 0
    global_width = 0

    card_base = None
    card_back = None

    font = None

    def __init__(self, pos: tuple, card_data: rules.basic.Card or None = None):
        """
        Initialize the card. Before initializing a card, the global size of the card class must be defined by calling
        the static `set_size` method.

        :param pos:
        :param card_data:
        """

        super().__init__()

        """
        Global scale
        """
        if Card.global_height <= 0:
            raise ValueError("the set_size method must be called before creating a card widget")

        """
        Sprite
        """
        self.card_front = Card.card_base.copy()

        self.image = Card.card_back
        self.rect = self.image.get_rect(center=pos)
        self.layer = Layer.CARD

        self.anim_group = AnimGroup()

        """
        Data field
        """
        self.card_data = card_data
        self.is_revealed = False

    def draw_card_front(self):
        """
        Draw the elements of the front side of the card:
        1. Rank
        2. Suit icon (top left corner)
        3. Suit icon (the big one)
        """

        if not self.card_data:
            raise AttributeError("cannot draw card if card data is not yet set")

        margin = 0.08 * self.card_front.get_width()

        """
        1. Rank text
        """
        rank_int = self.card_data.rank
        rank_char = rules.basic.RANK_CHARS[rank_int] if rank_int in rules.basic.RANK_CHARS else str(rank_int)
        rank_text_color = (0, 0, 0) if self.card_data.suit in ("S", "C") else (234, 61, 61)

        rank_text = Card.font.render(rank_char, True, rank_text_color)
        rank_text_rect = rank_text.get_rect(topleft=(margin, margin))
        self.card_front.blit(rank_text, rank_text_rect)

        """
        2. Top left corner suit
        """
        unscaled_suit = pygame.image.load(SUIT_SPRITE_PATHS[self.card_data.suit])
        corner_suit_size = 0.2 * self.card_front.get_width()

        corner_suit = pygame.transform.smoothscale(unscaled_suit, 2 * (corner_suit_size,))
        corner_suit_rect = corner_suit.get_rect(topleft=(margin, 2.5 * margin + corner_suit_size))
        self.card_front.blit(corner_suit, corner_suit_rect)

        """
        3. Middle suit
        """
        big_suit_size = 0.65 * self.card_front.get_width()
        big_suit_pos = self.card_front.get_width() - margin, self.card_front.get_height() - margin

        big_suit = pygame.transform.smoothscale(unscaled_suit, 2 * (big_suit_size,))
        big_suit_rect = big_suit.get_rect(bottomright=big_suit_pos)
        self.card_front.blit(big_suit, big_suit_rect)

    def reveal(self, duration=0.4):
        """
        Reveal the front side of the card with a card flip animation.
        """
        if duration <= 0:
            self.draw_card_front()
            self.image = self.card_front
            self.is_revealed = True

        else:
            animation = CardFlipAnimation(duration, self)
            self.anim_group.add(animation)

    @staticmethod
    def set_size(height):
        """
        All cards share the same images and font, which are stored globally. This is done in order to avoid rescaling
        the card image over and over again.

        The `set_size` method rescales those globally stored font and images the first time a card is created or
        whenever a card has a different size than the other.

        :param height:
        :return:
        """
        if height == Card.global_height:
            return
        elif height <= 0:
            raise ValueError("height must be a positive number")

        unscaled_base = pygame.image.load("assets/sprites/card/base.png")
        unscaled_back = pygame.image.load("assets/sprites/card/back.png")
        width = (unscaled_base.get_width() / unscaled_base.get_height()) * height

        Card.card_base = pygame.transform.smoothscale(unscaled_base, (width, height))
        Card.card_back = pygame.transform.smoothscale(unscaled_back, (width, height))

        Card.global_height = height
        Card.global_width = width

        Card.font = pygame.font.Font("assets/fonts/Archive-Regular.ttf", int(0.2 * height))

    def update(self, dt):
        self.anim_group.update(dt)