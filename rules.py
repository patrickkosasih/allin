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
* "S" : ♠ Spades
* "H" : ♥ Hearts
* "D" : ♦ Diamonds
* "C" : ♣ Clubs
"""

SUIT_CHARS = {"S": "♠",
              "H": "♥",
              "D": "♦",
              "C": "♣"}

RANK_CHARS = {1: "A",
              11: "J",
              12: "Q",
              13: "K"}


class Actions:
    FOLD = 0
    CHECK = 1
    CALL = 1
    BET = 2
    RAISE = 2


def card_str(card: Card):
    """
    Converts a `Card` namedtuple into a readable string format.
    Example: "6♦", "A♠", "Q♥".
    """
    return (RANK_CHARS[card.rank] if card.rank in RANK_CHARS else str(card.rank)) + SUIT_CHARS[card.suit]


class PlayerData:
    """
    The `PlayerData` class contains attributes of a player playing throughout the different hands of a poker game.

    The difference between this class to `PlayerHand` is that the attributes of this class is brought on through all
    the different hands of a game of poker, such as the amount of money.
    """

    def __init__(self, name: str, money: int):
        self.name = name
        self.money = money


class PlayerHand:
    """
    The `PlayerHand` class contains attributes that a player has for the current hand.

    The main difference between `PlayerData` and this class is that the attributes of this class is only relevant on
    the current hand, such as the pocket cards of a player.
    """

    def __init__(self, hand: "Hand", player_data: PlayerData):
        self.hand = hand
        self.player_data = player_data
        self.pocket_cards = []

        self.bet_amount = 0  # The amount of money spent on the current betting round
        self.folded = False
        self.called = False

    def bet(self, new_bet: int, blinds=False):
        """
        Pay an amount of money to match the bet of other players.

        :param new_bet: The equal bet amount.
        :param blinds: If set to True, then `called` will not be set to True. Used on the start of a hand where the
        two players with the blinds must bet an amount of money but still must call/check later.

        :return:
        """
        amount_to_pay = new_bet - self.bet_amount  # How much money to pay to call/raise

        if amount_to_pay >= self.player_data.money:
            # ALL IN
            amount_to_pay = self.player_data.money
            new_bet = self.player_data.money

        self.player_data.money -= amount_to_pay
        self.hand.pot += amount_to_pay
        self.bet_amount = new_bet

        if not blinds:
            self.called = True


class Hand:
    """
    An instance of the `Hand` class represents one hand/deal of a poker game. After a player wins a hand, another hand
    starts, but the game (`PokerGame`) is still the same.
    """

    def __init__(self, game: "PokerGame"):
        self.game = game
        self.players = [PlayerHand(hand=self, player_data=player) for player in game.players]
        # A list of `PlayerHand` instances based on the `PlayerData` list of the `PokerGame`.

        self.pot = 0
        self.bet_amount = self.game.sb_amount * 2

        self.community_cards = []
        self.deck = [Card(rank, suit) for suit in "SHDC" for rank in range(1, 14)]
        random.shuffle(self.deck)

        """
        Deal cards to players
        """
        n_dealed_cards = len(self.players) * 2

        dealed_cards = self.deck[:n_dealed_cards]
        self.deck = self.deck[n_dealed_cards:]

        for i, player in enumerate(self.players):
            player.pocket_cards = dealed_cards[i * 2 : i * 2 + 2]

        """
        Player turn initialization and blinds
        """
        self.current_turn = self.game.dealer
        self.blinds = sb, bb = self.get_next_turn(1), self.get_next_turn(2)

        self.players[sb].bet(self.game.sb_amount, blinds=True)
        self.players[bb].bet(self.game.sb_amount * 2, blinds=True)

        self.current_turn = self.get_next_turn(3)
        # The player with the first turn of a new hand is the player after the big blinds

    def action(self, action_type: int, new_amount=0):
        """
        Takes an action for the current turn player. There are 3 types of actions:
        1. Fold
        2. Check/call
        3. Bet/raise

        :param action_type: Determines the type of action using an integer value from the constants of the `Actions`
        class (0-2).

        :param new_amount: The amount of money to bet. Only used when the action type is to bet/raise.

        :return:
        """
        if type(action_type) is not int:
            raise TypeError("action type must be an int")
        elif action_type not in range(3):
            raise ValueError(f"action type must be 0, 1, or 2 (got: {action_type})")

        match action_type:
            case Actions.FOLD:   # Fold
                self.get_current_player().folded = True

            case Actions.CALL:   # Check/call
                self.get_current_player().bet(self.bet_amount)
                self.get_current_player().called = True

            case Actions.RAISE:  # Bet/raise
                if new_amount <= 2 * self.game.sb_amount:
                    raise ValueError("bet amount must be more than the minimum bet amount"
                                     f"({2 * self.game.sb_amount})")
                elif new_amount <= self.bet_amount:
                    raise ValueError("the new bet amount must be more than the previous betting amount "
                                     f"({self.bet_amount})")

                # Everyone except the betting/raising player must call again
                for x in self.players:
                    x.called = False

                self.bet_amount = new_amount
                self.get_current_player().bet(new_amount)

        if all(player.called for player in self.players if not player.folded):
            self.next_round()
        else:
            self.current_turn = self.get_next_turn()

    def next_round(self):
        """
        When everyone who is still in has bet the same amount, the game advances to the next betting round.

        :return:
        """
        for player in self.players:
            player.bet_amount = 0
            player.called = False

        self.bet_amount = 0
        self.current_turn = self.get_next_turn(1, turn=self.game.dealer)

        draw_n_cards = 3 if len(self.community_cards) == 0 else 1
        for _ in range(draw_n_cards):
            self.community_cards.append(self.deck.pop(0))

        print("NEXT BETTING ROUND")

    def get_next_turn(self, n=1, turn=-1, first_call=True) -> int:
        """
        Returns the player index after `n` turns of the current player turn.
        Players who have folded or are all-in are skipped.

        e.g. n = 2: returns the player index after 2 turns

        The `turn` argument may be passed in. If the `turn` argument is not passed in then this function uses the
        `self.current_turn` attribute.

        :param n: Number of turns after the specified turn
        :param turn: The current turn. If the argument is not passed in then the `self.current_turn` attribute is used.
        :param first_call: Always True when calling this function from outside, and then False for the recursions that
        follow. This is done so that the player of the `turn` parameter on the first call is not immediately skipped to
        the next player if the player on the first call has already folded/all-in.

        :return: The player index after `n` turns.
        """
        turn = self.current_turn if turn < 0 else turn

        if not first_call and (self.players[turn].folded or self.players[turn].player_data.money <= 0):
            return self.get_next_turn(n=n, turn=(turn + 1) % len(self.players), first_call=False)
        elif n <= 0:
            return turn
        else:
            return self.get_next_turn(n=n-1, turn=(turn + 1) % len(self.players), first_call=False)

    def get_current_player(self) -> PlayerHand:
        return self.players[self.current_turn]


class PokerGame:
    """
    An instance of `PokerGame` represents an ongoing poker game with multiple players. Throughout an ongoing game,
    there may be several hands/deals.
    """

    def __init__(self, n_players: int):
        # Note: In the future players may join in the middle of an ongoing match and the `n_players` parameter won't
        # be necessary.
        self.players = [PlayerData(f"Player {i + 1}", 1000) for i in range(n_players)]

        self.dealer = 0  # The index of `self.players` who becomes the dealer of the current hand.
        self.sb_amount = 25  # Small blinds amount. Big blinds = 2 * Small blinds.

        self.current_hand = Hand(self)

    def new_hand(self):
        # Cycle dealer
        self.dealer = (self.dealer + 1) % len(self.players)

        self.current_hand = Hand(self)
