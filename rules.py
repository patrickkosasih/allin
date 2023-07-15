"""
rules.py

Texas Hold'em Poker Rules Engine
by Patrick Kosasih
"""

import random
from collections import namedtuple
import functools

"""
==============
Card structure
==============
"""


Card = namedtuple("Card", ["rank", "suit"])
"""
The `Card` namedtuple is the basic data structure of a single card that consists of a rank and a suit.

The rank of a card is represented by an integer value between 2 to 14 inclusive. Number ranks (2-10) are directly
represented by the integer value, while letter ranks are represented by the numbers 11 to 14:
* 11 : J (Jack)
* 12 : Q (Queen)
* 13 : K (King)
* 14 : A (Ace)

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

RANK_CHARS = {11: "J",
              12: "Q",
              13: "K",
              14: "A"}


class Actions:
    FOLD = 0
    CHECK = 1
    CALL = 1
    BET = 2
    RAISE = 2


def card_str(card: Card) -> str:
    """
    Converts a `Card` namedtuple into a readable string format.
    Example: "6♦", "A♠", "Q♥".
    """
    return (RANK_CHARS[card.rank] if card.rank in RANK_CHARS else str(card.rank)) + SUIT_CHARS[card.suit]


def generate_deck() -> list:
    """
    Generates a shuffled deck of cards.
    """
    return [Card(rank, suit) for suit in "SHDC" for rank in range(2, 15)]


class HandRanking:
    """
    `HandRanking` is the class used to calculate hand rankings, the win condition for poker games.
    Hand rankings are not to be confused with rank (the value of a card).
    """

    """
    Ranking type constants
    Smaller number = Better rankings
    """
    # region Ranking type constants
    ROYAL_FLUSH = 1
    STRAIGHT_FLUSH = 2
    QUAD = 3
    FULL_HOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    TRIPLE = 7
    TWO_PAIR = 8
    PAIR = 9
    HIGH_CARD = 10
    # endregion

    RANK_COUNT_BASED = [
        QUAD,
        FULL_HOUSE,
        TRIPLE,
        TWO_PAIR,
        PAIR,
        HIGH_CARD
    ]
    """
    Rank count based hand rankings are rankings that are based on the number of cards of the same rank. For example,
    four of a kind (quad) is rank count based because there must be 4 cards of the same rank in order to achieve it,
    while straight is not rank count based because it's achieved by having 5 cards in consecutive order.
    """

    TYPE_STR = [
        "n/a",
        "royal flush",
        "straight flush",
        "four of a kind",
        "full house",
        "flush",
        "straight",
        "three of a kind",
        "two pair",
        "pair",
        "high card"
    ]
    """
    `TYPE_STR` converts a ranking type integer value (from the ranking type constants) into a readable string
    representing the name of the ranking type.
    """

    def __init__(self, cards: list[Card]):
        """
        Upon creating a new instance of `HandRankings`, the ranking is immediately calculated by calling the
        `calculate_ranking` method.

        :param cards: A list of cards, must be between 5 and 7 cards (inclusive) in length.
        """

        if len(cards) not in range(5, 8):
            raise ValueError("the list of cards must be 5-7 cards in length")

        self.cards = cards

        self.ranking_type = 0  # An integer representing the ranking type based on the ranking type constants.
                               # Smaller number = Better rankings

        self.ranked_cards = []
        self.kickers = []

        self.tiebreaker_score = 0

        self.calculate_ranking()

    def calculate_ranking(self):
        """
        Calculate the hand ranking of the given card combination, and then save the results to the fields of the class.

        There are 6 major steps to calculate a hand ranking:
        1. Count cards based on the rank and suit.
        2. Detect rank count based rankings.
        3. Detect straight rankings
        4. Detect flush
        5. Determine the ranked cards on rank count based rankings
        6. Calculate the tiebreaker score
        """

        """
        1. Count cards based on the rank and suit
        """
        # region Step 1
        rank_count = {}  # The number of cards for a certain rank.
        suit_count = {}  # The number of cards for a certain suit.

        for card in self.cards:
            rank_count[card.rank] = rank_count.setdefault(card.rank, 0) + 1
            suit_count[card.suit] = suit_count.setdefault(card.suit, 0) + 1
        # endregion Step 1

        """
        2. Detect rank count based rankings:
        * Four of a kind (quad)
        * Full house
        * Three of a kind (triple)
        * Two pair
        * One pair
        * High card
        
        Rank count based rankings are hand rankings that are based on the card count of the same rank. Detecting these
        rankings are done by making a sorted version of the `rank_count` dict, sorted from the highest card count of
        a rank. The hand ranking is then determined based on the highest count and the 2nd highest count of the sorted
        rank count.
        """
        # region Step 2
        sorted_rank_count = sorted(rank_count.items(), key=lambda x: x[1], reverse=True)
        # A list of (rank, number of cards of that rank) tuples sorted from the highest rank count.

        highest_count = sorted_rank_count[0][1]  # The highest number of cards of the same rank
        highest_count_2 = sorted_rank_count[1][1]  # The 2nd highest number of cards of the same rank

        match highest_count:
            case 4:
                self.ranking_type = HandRanking.QUAD

            case 3:
                if highest_count_2 >= 2:
                    self.ranking_type = HandRanking.FULL_HOUSE
                else:
                    self.ranking_type = HandRanking.TRIPLE

            case 2:
                if highest_count_2 >= 2:
                    self.ranking_type = HandRanking.TWO_PAIR
                else:
                    self.ranking_type = HandRanking.PAIR

            case 1:
                self.ranking_type = HandRanking.HIGH_CARD
        # endregion Step 2

        """
        3. Detect straight rankings:
        * Straight
        * Straight flush
        * Royal flush
        
        Straights are detected by creating a list of all the ranks sorted from the lowest, and then performing a linear
        scan to determine if there are 5 consecutive cards in a row or not.
        
        After detecting 5 consecutive cards, the program determines if those cards is a royal flush, straight flush, or
        just a regular straight; then those 5 cards are saved to the ranked cards list and the highest rank is saved as
        a tiebreaker score.
        
        If a sequence of 5 cards has already been found earlier, then the hand ranking, ranked cards, and tiebreaker
        score is only updated if the new hand is better than the previous one. This scenario can happen when there is a
        sequence of more than 5 cards (e.g. 3, 4, 5, 6, 7, 8).
        """
        # region Step 3
        sorted_ranks = sorted(rank_count.keys())  # A sorted list of all the available ranks

        if 14 in sorted_ranks:
            sorted_ranks.append(1)  # Aces can either be in the lowest or the highest card on a straight

        if len(sorted_ranks) >= 5:
            consecutives = [sorted_ranks[0]]
            # A list containing the rank of cards that are in consecutive order. If the next number on the sorted ranks
            # list breaks the sequence, then the consecutives list is reset.

            for x, y in zip(sorted_ranks[:-1], sorted_ranks[1:]):
                """
                Do a linear scan through the `sorted_ranks` list with 2 elements at a time. After a straight is found,
                the loop still continues because there may be another straight with a higher card.
                """
                if x + 1 == y:
                    consecutives.append(y)
                else:
                    consecutives = [y]

                if len(consecutives) >= 5:
                    """
                    If there are 5 cards with consecutive ranks, then it is a straight. The next step is to determine if
                    the straight is a straight flush, royal flush, or just a regular straight.
                    """
                    if len(consecutives) >= 6:
                        consecutives.pop(0)

                    # Determine the suit(s) of each rank in the straight sequence.
                    straight_suits = {rank: [] for rank in consecutives}
                    for card in self.cards:
                        if card.rank in straight_suits:
                            straight_suits[card.rank].append(card.suit)

                    matcher_suit = next(suits for suits in straight_suits.values() if len(suits) == 1)[0]
                    """`matcher_suit` is the suit of one of the cards in the straight cards. The suits of the other
                    cards on the straight sequence are then matched with the matcher suit, and if all of them match the
                    matcher suit, then it is a straight flush or royal flush.
                    
                    The matcher suit is chosen by taking the first rank in the sequence that only consists of a single
                    suit."""

                    for suits in straight_suits.values():
                        if matcher_suit not in suits:
                            self.ranking_type = min(self.ranking_type, HandRanking.STRAIGHT)

                            if self.ranking_type == HandRanking.STRAIGHT:
                                self.tiebreaker_score = y
                                self.ranked_cards = [next(card for card in self.cards if card.rank == rank)
                                                     for rank in consecutives]
                            break

                    else:
                        if y == 14:
                            self.ranking_type = HandRanking.ROYAL_FLUSH
                        else:
                            self.ranking_type = HandRanking.STRAIGHT_FLUSH

                        self.tiebreaker_score = y
                        self.ranked_cards = [next(card for card in self.cards
                                                  if card.rank == rank and card.suit == matcher_suit)
                                             for rank in consecutives]
        # endregion Step 3

        """
        4. Detect flush
        
        If there are more than 5 cards of the same suit, then it is a flush. If a better hand ranking (lower number in
        `self.ranking_type`) has already been found, then there is no need to detect for a flush.
        """
        # region Step 4
        if self.ranking_type > HandRanking.FLUSH and any(x >= 5 for x in suit_count.values()):
            self.ranking_type = min(self.ranking_type, HandRanking.FLUSH)

            flush_suit = next(suit for suit in suit_count if suit_count[suit] >= 5)
            self.ranked_cards = sorted([card for card in self.cards if card.suit == flush_suit], reverse=True)[:5]
        # endregion Step 4

        """
        5. Determine the ranked cards on rank count based rankings
        
        On rank count based hand rankings, the ranked cards are chosen based on the highest rank count; and also the 2nd
        highest rank count for full house and two pair. If the ranking is high card, the one and only ranked card is the
        card with the highest rank instead of the highest rank count.
        
        Each card of the hand is looped over in a list comprehension,
        and if the card is the rank with the highest card count, it is added to the ranked cards. If the ranking is a
        full house or two pair, the same thing is done for the 2nd highest rank count.
        
        If the number of ranked cards is still less than 5, then the unfilled slots are filled in by kickers, starting
        from the highest cards that are not part of the ranked cards. Kickers are saved in a separate list
        `self.kickers` instead of `self.ranked_cards`.
        """
        # region Step 5
        if self.ranking_type in HandRanking.RANK_COUNT_BASED:
            high_card = self.ranking_type == HandRanking.HIGH_CARD

            if not high_card:
                # The ranked cards are the highest number of cards with the same rank.
                self.ranked_cards = [card for card in self.cards if card.rank == sorted_rank_count[0][0]]

                if self.ranking_type in (HandRanking.FULL_HOUSE, HandRanking.TWO_PAIR):
                    # On full house and two pair, the 2nd highest number of card of the same rank is also part of the
                    # ranked cards.
                    self.ranked_cards += [card for card in self.cards if card.rank == sorted_rank_count[1][0]]

            sorted_rank_cards = iter(sorted((x for x in self.cards if x not in self.ranked_cards),
                                            key=lambda x: x.rank, reverse=True))
            """`sorted_rank_cards` is an iterator of cards sorted from the highest rank that are not part of the ranked
            cards."""

            if high_card:
                # High cards are separate because the only ranked card on a high card is not based on the sorted rank
                # count.
                self.ranked_cards = [next(sorted_rank_cards)]

            # The unfilled slots of the 5 card hand are saved as kickers.
            while len(self.ranked_cards) + len(self.kickers) < 5:
                self.kickers.append(next(sorted_rank_cards))
        # endregion Step 5

        """
        6. Calculate the tiebreaker score
        
        The tiebreaker score is used to determine which player wins if there are more than one player with the same
        winning hand ranking. Higher tiebreaker score = Better hand. Keep in mind that a better hand ranking type still
        beats a higher tiebreaker score.
        
        ==============================
        The Tiebreaker Score Algorithm
        ==============================
        
        The tiebreaker score is calculated by having a tiebreaker list. The tiebreaker list consists of cards
        ordered from the most significant card to the least significant; or to put it in other words, the first card of
        the tiebreaker list gives more influence to the tiebreaker score than the other cards that follow.
        
        Determining the tiebreaker list:
        * Straight rankings (straight, straight flush, and royal flush):
            The tiebreaker score for straight rankings is simply the rank of the highest card, and has already been
            determined before. Step 6 is skipped.
            
        * Flush:
            The tiebreaker score for a flush is the ranked cards, sorted from the highest rank.
            
        * Rank count based rankings:
            The tiebreaker list consists of the first and last cards of the ranked cards list, and the kickers list.
            On two pairs, the first element of the tiebreaker list must be the rank of the higher pair, so if the first
            card of the ranked cards list is lower than the last, they are swapped.
        
        After determining the tiebreaker list, the next step is to reduce it to an integer value. The ranks of every
        card are bit shifted 4 bits to the right (same as multiplying by 16) and then added by the next value. The
        reducing of the tiebreaker list is just like treating every rank as base-16/hexadecimal digits and constructing
        a hexadecimal number out of it. For example, if the tiebreaker list is [8♥, 2♦, Q♣], then the tiebreaker score
        would be the hexadecimal number 0x82C (C because queens are represented by 12), which is 2092.
        """
        # region Step 6
        if self.tiebreaker_score == 0:
            if self.ranking_type == HandRanking.FLUSH:
                tiebreaker_list = self.ranked_cards

            else:
                tiebreaker_list = [self.ranked_cards[0], self.ranked_cards[-1]] + self.kickers

                if self.ranking_type == HandRanking.TWO_PAIR and tiebreaker_list[0] < tiebreaker_list[1]:
                    tiebreaker_list[0], tiebreaker_list[1] = tiebreaker_list[1], tiebreaker_list[0]

            # print(" ".join([card_str(card) for card in tiebreaker_list]))

            self.tiebreaker_score = functools.reduce(lambda x, y: (x << 4) + y, (z.rank for z in tiebreaker_list))
        # endregion Step 6


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
    the current deal, such as the pocket cards of a player.
    """

    def __init__(self, deal: "Deal", player_data: PlayerData):
        self.deal = deal
        self.player_data = player_data
        self.pocket_cards = []

        self.bet_amount = 0  # The amount of money spent on the current betting round
        self.folded = False
        self.called = False

    def bet(self, new_bet: int, blinds=False):
        """
        Pay an amount of money to match the bet of other players.

        :param new_bet: The equal bet amount.
        :param blinds: If set to True, then `called` will not be set to True. Used on the start of a deal where the
        two players with the blinds must bet an amount of money but still must call/check later.

        :return:
        """
        amount_to_pay = new_bet - self.bet_amount  # How much money to pay to call/raise

        if amount_to_pay >= self.player_data.money:
            # ALL IN
            amount_to_pay = self.player_data.money
            new_bet = self.player_data.money

        self.player_data.money -= amount_to_pay
        self.deal.pot += amount_to_pay
        self.bet_amount = new_bet

        if not blinds:
            self.called = True


class Deal:
    """
    An instance of the `Deal` class represents one hand/deal of a poker game. After a player wins a deal, another deal
    starts, but the game (`PokerGame`) is still the same.
    """

    def __init__(self, game: "PokerGame"):
        self.game = game
        self.players = [PlayerHand(deal=self, player_data=player) for player in game.players]
        # A list of `PlayerHand` instances based on the `PlayerData` list of the `PokerGame`.

        self.pot = 0
        self.bet_amount = self.game.sb_amount * 2

        self.community_cards = []
        self.deck = generate_deck()
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
        # The player with the first turn of a new deal is the player after the big blinds

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
    there may be several deals.
    """

    def __init__(self, n_players: int):
        # Note: In the future players may join in the middle of an ongoing match and the `n_players` parameter won't
        # be necessary.
        self.players = [PlayerData(f"Player {i + 1}", 1000) for i in range(n_players)]

        self.dealer = 0  # The index of `self.players` who becomes the dealer of the current deal.
        self.sb_amount = 25  # Small blinds amount. Big blinds = 2 * Small blinds.

        self.current_deal = Deal(self)

    def new_deal(self):
        # Cycle dealer
        self.dealer = (self.dealer + 1) % len(self.players)

        self.current_deal = Deal(self)
