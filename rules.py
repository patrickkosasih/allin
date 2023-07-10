"""
rules.py

Texas Hold'em Poker Rules Engine
by Patrick Kosasih
"""

import random
from collections import namedtuple


Card = namedtuple("Card", ["rank", "suit"])
"""
The `Card` namedtuple is the basic data structure of a single card that consists of a rank and a suit.

The rank of a card is represented by an integer value between 1 to 13 inclusive. Number ranks (2-10) are straight
forward, while letter ranks are represented by the numbers 1, 11, 12, and 13:
* 1  : A (Ace)
* 11 : J (Jack)
* 12 : Q (Queen)
* 13 : K (King)

The suit of a card is represented by a single character, which is the initial letter of the suit name.
* "S" : Spades
* "H" : Hearts
* "D" : Diamonds
* "C" : Clubs
"""

SUIT_CHARS = {"S": "♠",
              "H": "♥",
              "D": "♦",
              "C": "♣"}

RANK_CHARS = {1: "A",
              11: "J",
              12: "Q",
              13: "K"}


def card_str(card: Card):
    """
    Converts a `Card` namedtuple into a readable string format.
    Example: "6♦", "A♠", "Q♥".
    """
    return (RANK_CHARS[card.rank] if card.rank in RANK_CHARS else str(card.rank)) + SUIT_CHARS[card.suit]


class PlayerData:
    """
    The `PlayerData` class contains attributes of a player playing throughout the different hands of a poker game.
    """

    def __init__(self):
        self.money = 1000


class PlayerHand:
    """
    The `PlayerHand` class contains attributes that a player has for the current hand.

    The main difference between `PlayerData` and this class is that the attributes of this class is only relevant on
    the current hand, such as the pocket cards of a player.
    """

    def __init__(self, player_data: PlayerData):
        self.player_data = player_data
        self.pocket_cards = []
        self.bet_amount = 0
        self.folded = False

    def bet(self, new_amount: int):
        self.player_data.money -= new_amount - self.bet_amount
        self.bet_amount = new_amount


class Hand:
    """
    An instance of the `Hand` class represents one hand/deal of a poker game. After a player wins a hand, another hand
    starts, but the game (`PokerGame`) is still the same.
    """

    def __init__(self, game: "PokerGame"):
        self.game = game
        self.player_hands = [PlayerHand(player) for player in game.players]

        self.pot = 0
        self.community_cards = []

        self.deck = [Card(rank, suit) for suit in "SHDC" for rank in range(1, 14)]
        random.shuffle(self.deck)

        """
        Deal cards to players
        """
        n_dealed_cards = len(self.player_hands) * 2

        dealed_cards = self.deck[:n_dealed_cards]
        self.deck = self.deck[n_dealed_cards:]

        for i, player in enumerate(self.player_hands):
            player.pocket_cards = dealed_cards[i * 2 : i * 2 + 2]


class PokerGame:
    """
    An instance of `PokerGame` represents an ongoing poker game with multiple players. Throughout an ongoing game,
    there may be several hands/deals.
    """

    def __init__(self, n_players: int):
        # Note: In the future players may join in the middle of an ongoing match and the `n_players` parameter won't
        # be necessary.
        self.players = [PlayerData() for _ in range(n_players)]
        self.dealer = 0
        self.hand: Hand = Hand(self)

    def new_hand(self):
        # Cycle dealer
        self.dealer = (self.dealer + 1) % len(self.players)
        self.hand = Hand(self)
