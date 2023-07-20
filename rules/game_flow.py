"""
rules/game_flow.py

The module that controls the flow of a poker game.

This module contains classes and methods that handle the flow of a poker game, so that every player action follows the
rules of Texas Hold'em poker.
"""

from rules.basic import *


class Actions:
    FOLD = 0
    CHECK = 1
    CALL = 1
    BET = 2
    RAISE = 2


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
        self.hand_ranking = HandRanking()

        self.bet_amount = 0  # The amount of money spent on the current betting round
        self.last_action = ""  # A string representing the action the player previously made.
        self.folded = False
        self.called = False
        self.all_in = False

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
            self.last_action = "all-in"
            self.all_in = True

            amount_to_pay = self.player_data.money
            new_bet = amount_to_pay + self.bet_amount

        self.player_data.money -= amount_to_pay
        self.deal.pot += amount_to_pay
        self.bet_amount = new_bet

        if blinds:
            if not self.all_in:
                self.last_action = "bet"
        else:
            self.called = True


class Deal:
    """
    An instance of the `Deal` class represents one hand/deal of a poker game. After a player wins a deal, another deal
    starts, but the game (`PokerGame`) is still the same.
    """

    def __init__(self, game: "PokerGame"):
        if len(game.players) < 2:
            raise ValueError("there must be at least 2 players to start a deal")

        self.game = game
        self.players = [PlayerHand(deal=self, player_data=player) for player in game.players]
        # A list of `PlayerHand` instances based on the `PlayerData` list of the `PokerGame`.
        self.winners = []

        self.pot = 0
        self.bet_amount = self.game.sb_amount * 2

        self.community_cards = []
        self.deck = generate_deck()

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
        elif self.winners:
            raise StopIteration("this deal has already been concluded")

        match action_type:
            case Actions.FOLD:   # Fold
                self.get_current_player().folded = True
                self.get_current_player().last_action = "fold"

                # If everyone except one player folds, then that player wins.
                if sum(not player.folded for player in self.players) == 1:
                    self.showdown()

            case Actions.CALL:   # Check/call
                # Set action text
                if self.bet_amount > 0:
                    self.get_current_player().last_action = "call"
                else:
                    self.get_current_player().last_action = "check"

                self.get_current_player().bet(self.bet_amount)
                self.get_current_player().called = True

            case Actions.RAISE:  # Bet/raise
                if new_amount < 2 * self.game.sb_amount:
                    raise ValueError("bet amount must be more than the minimum bet amount "
                                     f"({2 * self.game.sb_amount})")

                elif new_amount <= self.bet_amount:
                    raise ValueError("the new bet amount must be more than the previous betting amount "
                                     f"({self.bet_amount})")

                elif new_amount > self.get_current_player().player_data.money + self.bet_amount:
                    # raise ValueError("bet amount must not be more than the money left "
                    #                  f"({self.get_current_player().player_data.money})")
                    new_amount = self.get_current_player().player_data.money + self.bet_amount  # ALL-IN

                # Everyone except the betting/raising player must call again
                for x in self.players:
                    x.called = False

                # Set action text
                if self.bet_amount > 0:
                    self.get_current_player().last_action = "raise"
                else:
                    self.get_current_player().last_action = "bet"

                self.bet_amount = new_amount
                self.get_current_player().bet(new_amount)

        if all(player.called or player.all_in for player in self.players if not player.folded):
            self.next_round()
        else:
            self.current_turn = self.get_next_turn()

    def next_round(self):
        """
        When everyone who is still in has bet the same amount, the game advances to the next betting round.

        :return:
        """

        self.bet_amount = 0
        self.current_turn = self.get_next_turn(1, turn=self.game.dealer)

        if len(self.community_cards) < 5:
            draw_n_cards = 3 if len(self.community_cards) == 0 else 1
            for _ in range(draw_n_cards):
                self.community_cards.append(self.deck.pop(0))
        else:
            self.showdown()

        for player in self.players:
            player.hand_ranking = HandRanking(self.community_cards + player.pocket_cards)
            player.bet_amount = 0
            player.last_action = "folded" if player.folded else ("all-in" if player.all_in else "")
            player.called = False

    def showdown(self):
        """
        Decide the winner of the current deal with a showdown.
        Can also be used when there is only 1 player left who hasn't folded.
        """
        not_folded = [player for player in self.players if not player.folded]

        max_score = max(player.hand_ranking.overall_score for player in not_folded)
        self.winners = [player for player in not_folded if player.hand_ranking.overall_score == max_score]

        for winner in self.winners:
            winner.player_data.money += self.pot // len(self.winners)

    def get_next_turn(self, n=1, turn=-1) -> int:
        """
        Returns the player index after `n` turns of the current player turn.
        Players who have folded or are all-in are skipped.

        e.g. n = 2: returns the player index after 2 turns

        The `turn` argument may be passed in. If the `turn` argument is not passed in then this function uses the
        `self.current_turn` attribute.

        :param n: Number of turns after the specified turn
        :param turn: The current turn. If the argument is not passed in then the `self.current_turn` attribute is used.

        :return: The player index after `n` turns.
        """
        turn = self.current_turn if turn < 0 else turn

        if sum(not player.folded for player in self.players) <= 1 or \
            all(player.all_in for player in self.players if not player.folded):
            return turn
        else:
            return self.__get_next_turn(n=n - 1, turn=(turn + 1) % len(self.players))

    def __get_next_turn(self, n=1, turn=-1):
        if self.players[turn].folded or self.players[turn].all_in:
            # If player is folded/all-in then skip to the next player
            return self.__get_next_turn(n=n, turn=(turn + 1) % len(self.players))

        elif n <= 0:
            # Get current turn
            return turn

        else:
            # Get next turn
            return self.__get_next_turn(n=n-1, turn=(turn + 1) % len(self.players))

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

        self.deal = Deal(self)

    def new_deal(self):
        self.players = [player for player in self.players if player.money > 0]  # Remove bankrupt players
        self.dealer = (self.dealer + 1) % len(self.players)  # Cycle dealer

        if len(self.players) >= 2:
            self.deal = Deal(self)
