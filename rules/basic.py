"""
rules/basic.py

The module that contains two essential building blocks for the rules engine of poker:

1. Card
    The `Card` namedtuple is the basic data structure of a card.

2. HandRanking
    The `HandRanking` class is used to calculate the ranking of a hand; the win condition for a game of poker.
"""

import functools
import random
from collections import namedtuple


"""
=================
I. Card structure
=================
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
    deck = [Card(rank, suit) for suit in "SHDC" for rank in range(2, 15)]
    random.shuffle(deck)
    return deck


"""
=====================
II. HandRanking class
=====================
"""


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

    def __init__(self, cards: list[Card] = None):
        """
        Upon creating a new instance of `HandRankings`, the ranking is immediately calculated by calling the
        `calculate_ranking` method.

        :param cards: A list of cards, must be between 5 and 7 cards (inclusive) in length. It is also possible to not
        pass in the `cards` argument; doing so will skip the `calculate_ranking` process.
        """
        self.cards = cards

        self.ranking_type = 0  # An integer representing the ranking type based on the ranking type constants.
        # Smaller number = Better rankings

        self.ranked_cards = []
        self.kickers = []

        self.tiebreaker_score = 0
        self.overall_score = 0

        if cards:
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

        if len(self.cards) not in range(5, 8):
            raise ValueError("the list of cards must be 5-7 cards in length")

        """
        1. Count cards based on the rank and suit
        """
        # region Step 1
        rank_count = {}  # The number of cards for a certain rank. Structure: {rank: number of cards of that rank}
        suit_count = {}  # The number of cards for a certain suit. Structure: {suit: number of cards of that suit}

        for card in self.cards:
            rank_count[card.rank] = rank_count.setdefault(card.rank, 0) + 1
            suit_count[card.suit] = suit_count.setdefault(card.suit, 0) + 1

        sorted_rank_count = sorted(rank_count.items(), key=lambda x: (x[1] << 4) + x[0], reverse=True)
        """
        `sorted_rank_count` is a list of tuples from `rank_count.items()` dict. The (rank, rank count) pairs/tuples
        are sorted from the highest rank count, then the same rank counts are sorted from the highest rank.

        To do so, the key of the sorting is `lambda x: (x[1] << 4) + x[0]` as seen above. The rank count (x[1]) is bit
        shifted 4 bits to the left (multiplied by 16) and then added by the rank (x[0]) so that the tuples are sorted
        by the rank count first and then by the rank.
        """
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
            sorted_ranks.insert(0, 1)  # Aces can either be in the lowest or the highest card on a straight

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

                    if consecutives[0] == 1:
                        # If the first card of the straight is an ace (the lowest possible straight) then change the
                        # rank integer from 1 back to 14
                        consecutives[0] = 14

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
            self.ranking_type = HandRanking.FLUSH

            flush_suit = next(suit for suit in suit_count if suit_count[suit] >= 5)
            self.ranked_cards = sorted([card for card in self.cards if card.suit == flush_suit], reverse=True)[:5]
            # The ranked cards list is sorted from the highest cards with the flush suit (the suit with 5 or more
            # cards). Only the 5 highest cards are saved.

        # endregion Step 4

        """
        5. Determine the ranked cards on rank count based rankings

        If the best hand ranking found is a rank count based ranking, then the ranked cards are determined in this step.
        Otherwise, this step is skipped.

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
            # The ranked cards are the highest number of cards with the same rank.
            self.ranked_cards = [card for card in self.cards if card.rank == sorted_rank_count[0][0]]

            if self.ranking_type in (HandRanking.FULL_HOUSE, HandRanking.TWO_PAIR):
                # On full house and two pair, the 2nd highest number of card of the same rank is also part of the
                # ranked cards.
                self.ranked_cards += [card for card in self.cards if card.rank == sorted_rank_count[1][0]]

            self.kickers = sorted((x for x in self.cards if x not in self.ranked_cards),
                                  key=lambda x: x.rank, reverse=True)[:5 - len(self.ranked_cards)]
            """
            The kickers are the first n cards that are not part of the ranked cards, sorted from the highest.
            n being `5 - len(self.ranked_cards)` so that the length of kickers + length of ranked cards = 5.
            """

        # endregion Step 5

        """
        6. Calculate the tiebreaker score and overall score

        The tiebreaker score is used to determine which player wins if there are more than one player with the same
        winning hand ranking. Higher tiebreaker score = Better hand. Keep in mind that a better hand ranking type still
        beats a higher tiebreaker score.

        After calculating the tiebreaker score, the overall score is determined. The overall score is based on both the
        ranking type and the tiebreaker score. The player(s) with the highest overall score wins the hand.

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
            This is possible because the ranked cards list has already been sorted previously so that the first card on
            the list is always the prioritized one. For example, on a full house, the three cards of the same rank has
            more influence in the tiebreak, and on the ranked cards list, the three cards are already put before the two
            other cards.

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

            # print(" ".join([card_str(card) for card in tiebreaker_list]))

            self.tiebreaker_score = functools.reduce(lambda x, y: (x << 4) + y, (z.rank for z in tiebreaker_list))

        self.overall_score = ((10 - self.ranking_type) << 24) + self.tiebreaker_score
        # endregion Step 6

