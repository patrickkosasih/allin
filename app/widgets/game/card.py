import pygame

import rules.basic
from app.animations.var_slider import VarSlider
from app.audio import play_sound
from app.shared import Layer
from app.animations.card_flip import CardFlipAnimation
from app.widgets.widget import Widget

SUIT_SPRITE_PATHS = {
    "S": "assets/sprites/card/spades.png",
    "H": "assets/sprites/card/hearts.png",
    "D": "assets/sprites/card/diamonds.png",
    "C": "assets/sprites/card/clubs.png"
}


class Card(Widget):
    """
    The card sprite represents a single card, whether it's a pocket card or a community card.

    The `Card` class has some global attributes, which means some properties of a card share the same global variable.
    """

    # Global dimensions
    global_height = 0
    global_width = 0

    # Shared image objects
    card_base = None
    card_back = None
    highlight = None
    k_highlight = None

    # Shared font object
    font = None

    def __init__(self, parent, x, y, unit="px", anchor="tl", pivot="ctr", card_data: rules.basic.Card or None = None):
        """
        Initialize the card. Before initializing a card, the global size of the card class must be defined by calling
        the static `set_size` method.
        """

        if Card.global_height <= 0:
            raise ValueError("the set_size method must be called before creating a card widget")


        super().__init__(parent, x, y, self.global_width, self.global_height, unit, anchor, pivot)

        """
        Sprite
        """
        self.card_front = Card.card_base.copy()

        self._image = Card.card_back
        self.layer = Layer.CARD

        """
        Data fields
        """
        self.card_data = card_data
        self.is_revealed = False

        """
        Highlight
        """
        self.is_highlighted = False
        self.is_ranked = False

    def draw_card_front(self):
        """
        Draw the elements of the front side of the card:
        1. Rank
        2. Suit icon (top left corner)
        3. Suit icon (the big one)
        """

        if not self.card_data:
            raise AttributeError("cannot draw card if card data is not yet set")

        margin = 0.09 * self.card_front.get_width()

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

    def reveal(self, duration=0.4, sfx=True):
        """
        Reveal the front side of the card with a card flip animation.
        """

        if duration <= 0:
            self.draw_card_front()
            self.image = self.card_front.copy()
            self.is_revealed = True
        else:
            animation = CardFlipAnimation(duration, self)
            self.scene.anim_group.add(animation)

        if sfx:
            play_sound("assets/audio/game/card/flip.mp3")

    def set_highlight_alpha(self, alpha: int):
        """
        Set the alpha value of the highlight and update the sprite image. The highlight is drawn to the sprite image
        using blit instead of using different sprite objects and sprite groups.
        """

        hl = (Card.highlight if self.is_ranked else Card.k_highlight).copy()
        hl.set_alpha(alpha)

        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.card_front, (0, 0))
        self.image.blit(hl, (0, 0))

    def show_highlight(self, shown: bool, ranked: bool = False):
        """
        Highlight the card using a green/gray colored border around the card.

        :param shown: True: Highlight the card; False: Unhighlight the card.
        :param ranked: True: Green border for ranked cards; False: Gray border for kicker cards.
        """

        if shown and not self.is_revealed:
            raise AttributeError("cannot highlight an unrevealed card")
        elif shown == self.is_highlighted:
            return

        self.is_highlighted = shown
        self.is_ranked = ranked if shown else self.is_ranked

        start_end = (0, 255) if shown else (255, 0)
        VarSlider(0.25, *start_end, setter_func=lambda x: self.set_highlight_alpha(int(x)),
                  anim_group=self.scene.anim_group)


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
        unscaled_highlight = pygame.image.load("assets/sprites/card/highlight.png")
        unscaled_k_highlight = pygame.image.load("assets/sprites/card/kicker highlight.png")

        width = (unscaled_base.get_width() / unscaled_base.get_height()) * height

        Card.card_base = pygame.transform.smoothscale(unscaled_base, (width, height))
        Card.card_back = pygame.transform.smoothscale(unscaled_back, (width, height))
        Card.highlight = pygame.transform.smoothscale(unscaled_highlight, (width, height))
        Card.k_highlight = pygame.transform.smoothscale(unscaled_k_highlight, (width, height))

        Card.global_height = height
        Card.global_width = width

        Card.font = pygame.font.Font("assets/fonts/Archive-Regular.ttf", int(0.2 * height))
