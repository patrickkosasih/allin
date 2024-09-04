"""
rules/game_flow.py

The module that controls the flow of a poker game. This module contains classes and methods that handle the flow of a
poker game, so that every player action follows the rules of Texas Hold'em poker.
"""
from dataclasses import dataclass

from rules.basic import *


class Actions:
    FOLD = 0
    CHECK = 1
    CALL = 1
    BET = 2
    RAISE = 2


class ActionResult:
    """
    The `ActionResult` class contains return codes for the `action` method of `Deal`.
    """
    SUCCESS = 0
    LESS_THAN_MIN_BET = 1
    LESS_THAN_MIN_RAISE = 2
    ROUND_ALREADY_ENDED = 3
    DEAL_ALREADY_ENDED = 4
    DEAL_NOT_STARTED_YET = 5


@dataclass
class GameEvent:
    """
    A game event is used to pass information from an ongoing game/deal to the `receive_event` method of a `Player`
    object. The information can then be used to update the GUI, call the action method of a bot, and more.
    """

    # Event codes
    DEFAULT_ACTION = 0
    NEW_DEAL = 1
    START_DEAL = 2
    ROUND_FINISH = 3
    NEW_ROUND = 4
    START_NEW_ROUND = 5
    SKIP_ROUND = 6
    DEAL_END = 7
    RESET_DEAL = 8
    RESET_PLAYERS = 9

    # Class fields
    code: int
    prev_player: int = -1
    next_player: int = -1
    message: str = ""
    bet_amount: int = 0


class Player:
    """
    The `Player` class is the player controller class for a single player. Previously known as a player data.
    It also contains attributes of a player playing throughout the different hands of a poker game. An instance of this
    class can be a real player that can control their actions, or even a bot.

    The difference between this class to `PlayerHand` is that the attributes of this class is brought on through all
    the different deals of a game of poker, such as the amount of money.

    Some methods of this class are empty and can be altered in a subclass of `Player` for an interface to actions on the
    game.
    """

    def __init__(self, game: "PokerGame", name: str, money: int):
        self.game = game
        self.player_hand = None

        self.name = name
        self.money = money
        self.player_number = -2  # -2: Not assigned to any PokerGame

    def action(self, action_type: int, new_amount=0) -> GameEvent or None:
        """
        Calls the `self.game.deal.action()` method along with its arguments, but only if it's currently this player's
        turn and the deal is not over.

        :return: An `ActionResult` object; `None` if it's not this player's turn.
        """
        if self.game.deal.get_current_player().player_data is self and not self.game.deal.winners:
            action_result = self.game.deal.action(action_type, new_amount)
            return action_result
        else:
            return None

    # Hook method: Can be overridden by subclasses as an interface.
    def receive_event(self, game_event: GameEvent):
        """
        A hook method that is called every time any player makes an action.
        """
        pass


class PlayerHand:
    """
    The `PlayerHand` class contains attributes that a player has for the current hand.

    The main difference between `Player` and this class is that the attributes of this class is only relevant on
    the current deal, such as the pocket cards of a player. The `Player` instance can also be accessed by referencing
    the `player_data` attribute.
    """

    def __init__(self, deal: "Deal", player_data: Player):
        self.deal = deal
        self.player_data = player_data

        self.player_data.player_hand = self
        """
        When creating a `PlayerHand` object, the player hand attribute of the player data gets updated; creating a
        circular reference between the two.
        """

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
            """
            ALL IN
            """
            self.all_in = True

            amount_to_pay = self.player_data.money
            new_bet = amount_to_pay + self.bet_amount

        self.player_data.money -= amount_to_pay
        self.deal.pot += amount_to_pay
        self.bet_amount = new_bet

        if blinds:
            self.last_action = "bet" if not self.all_in else "all in"
        else:
            self.called = True


class Deal:
    """
    An instance of the `Deal` class represents one hand/deal of a poker game. After a player wins a deal, another deal
    starts, but the game (`PokerGame`) is still the same.
    """

    def __init__(self, game: "PokerGame"):
        """
        Initialize the fields of a deal, notably the `PlayerHand` objects and their pocket cards. After initializing the
        deal, the `start_deal` is separately called to start the deal.

        :param game: The parent `PokerGame` object
        """

        if len(game.players) < 2:
            raise ValueError("there must be at least 2 players to start a deal")

        self.game = game
        self.players = [PlayerHand(deal=self, player_data=player) for player in game.players]
        # A list of `PlayerHand` instances based on the `PlayerData` list of the `PokerGame`.
        self.winners = []
        # A list of `PlayerHand` objects who won the deal. If the deal is still ongoing then the list is empty.

        self.pot = 0
        self.bet_amount = 0

        self.community_cards = []
        self.deck = generate_deck()

        self.current_turn = self.get_next_turn(n=1, turn=self.game.dealer) if len(self.players) > 2 else self.game.dealer
        self.blinds = (self.current_turn, self.get_next_turn(1))

        self.round_finished = False
        self.deal_started = False
        self.skip_next_rounds = False

        """
        Deal cards to players
        """
        n_dealed_cards = len(self.players) * 2

        dealed_cards = self.deck[:n_dealed_cards]
        self.deck = self.deck[n_dealed_cards:]

        for i, player in enumerate(self.players):
            player.pocket_cards = dealed_cards[i * 2: i * 2 + 2]

    def start_deal(self):
        """
        Start the current deal. Only called once on the start of a deal.
        """

        self.deal_started = True

        """
        Player turn initialization and blinds
        """
        self.action(Actions.BET, self.game.sb_amount, blinds=True)
        self.action(Actions.BET, self.game.sb_amount * 2, blinds=True)

    def action(self, action_type: int, new_amount=0, blinds=False) -> int:
        """
        Takes an action for the current turn player. There are 3 types of actions:
        1. Fold
        2. Check/call
        3. Bet/raise

        :param action_type: Determines the type of action using an integer value from the constants of the `Actions`
        class (0-2).

        :param new_amount: The amount of money to bet. Only used when the action type is to bet/raise.

        :param blinds: Used for automatically betting the small and big blinds on the beginning of a deal.

        :return: An action result integer code.
        """

        if type(action_type) is not int:
            raise TypeError("action type must be an int")
        elif action_type not in range(3):
            raise ValueError(f"action type must be 0, 1, or 2 (got: {action_type})")
        elif self.round_finished:
            return ActionResult.ROUND_ALREADY_ENDED
        elif self.winners:
            return ActionResult.DEAL_ALREADY_ENDED
        elif not self.deal_started:
            return ActionResult.DEAL_NOT_STARTED_YET

        player: PlayerHand = self.get_current_player()

        action_broadcast = GameEvent(code=GameEvent.DEFAULT_ACTION if not blinds else GameEvent.START_DEAL,
                                     prev_player=self.current_turn,
                                     next_player=self.get_next_turn(),
                                     message="")

        """
        Do the action
        """
        # region Do the action
        match action_type:
            case Actions.FOLD:   # Fold
                player.folded = True
                action_broadcast.message = "fold"
                action_broadcast.bet_amount = player.bet_amount

                # If everyone except one player folds, then that player wins.
                if sum(not player.folded for player in self.players) == 1:
                    self.showdown()


            case Actions.CALL:   # Check/call
                # Set action text
                if self.bet_amount > 0:
                    action_broadcast.message = "call"
                else:
                    action_broadcast.message = "check"

                player.bet(self.bet_amount)
                player.called = True
                action_broadcast.bet_amount = self.bet_amount

            case Actions.RAISE:  # Bet/raise
                if new_amount >= player.player_data.money + player.bet_amount:
                    new_amount = player.player_data.money + player.bet_amount  # ALL IN

                elif not blinds and new_amount < self.game.min_bet:
                    return ActionResult.LESS_THAN_MIN_BET

                elif new_amount < 2 * self.bet_amount:
                    return ActionResult.LESS_THAN_MIN_RAISE

                # Everyone except the betting/raising player must call again
                for x in self.players:
                    x.called = False

                # Set action text
                if self.bet_amount > 0 and not blinds:
                    action_broadcast.message = "raise"
                else:
                    action_broadcast.message = "bet"

                player.bet(new_amount, blinds)
                if not blinds:
                    # Update the bet amount of the current round to the new amount.
                    # Unless the bet is part of the blinds.
                    self.bet_amount = new_amount

                action_broadcast.bet_amount = player.bet_amount
        # endregion

        if player.all_in:
            action_broadcast.message = "all in"

        player.last_action = action_broadcast.message

        """
        After the action
        
        1. If everyone who hasn't folded has called or is all in, then the deal advances to the next betting round.
           Advancing to the next betting round is done separately by calling the `start_new_round` method
        2. Otherwise, cycle the current turn to the next player.
        """
        if all(player.called or player.all_in for player in self.players if not player.folded):
            action_broadcast.code = GameEvent.ROUND_FINISH
            action_broadcast.next_player = -1
            self.round_finished = True

        else:
            self.current_turn = self.get_next_turn()

        """
        Broadcast the game event
        """
        self.broadcast(action_broadcast)

        return ActionResult.SUCCESS

    def next_round(self):
        """
        Advance to the next betting round by resetting the round and revealing the next community card.

        :return:
        """

        if self.winners:
            return

        """
        Reset fields
        """
        self.bet_amount = 0
        self.current_turn = self.get_next_turn(1, turn=self.game.dealer)
        self.round_finished = False

        """
        Reveal community cards or showdown
        """
        if len(self.community_cards) < 5:
            draw_n_cards = 3 if len(self.community_cards) == 0 else 1
            for _ in range(draw_n_cards):
                self.community_cards.append(self.deck.pop(0))
        else:
            self.showdown()
            return

        """
        Reset player hands
        """
        for player in self.players:
            player.hand_ranking = HandRanking(self.community_cards + player.pocket_cards)
            player.bet_amount = 0
            player.last_action = "folded" if player.folded else ("all-in" if player.all_in else "")
            player.called = False

        """
        Broadcast game event
        """
        if sum(not player.all_in for player in self.players if not player.folded) <= 1:
            # If everyone who are still in are all-in (except 1 player or less), then the next betting round is skipped.
            self.skip_next_rounds = True
            self.broadcast(GameEvent(GameEvent.SKIP_ROUND, -1, -1, ""))

        else:
            # Broadcast round event
            self.broadcast(GameEvent(GameEvent.NEW_ROUND, -1, -1, ""))

    def start_new_round(self):
        """
        Start the new betting round by broadcasting the "start round" game event to all players. This function
        should be only called after calling the `next_round` method.
        """

        if not self.skip_next_rounds and not self.winners:
            self.round_finished = False
            self.broadcast(GameEvent(GameEvent.START_NEW_ROUND, -1, self.current_turn, ""))

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

        self.broadcast(GameEvent(GameEvent.DEAL_END, -1, -1, ""))

    def broadcast(self, broadcast: GameEvent) -> None:
        """
        Broadcast a `GameEvent` to all `Player` objects by calling their `receive_event` methods.
        """
        self.game.broadcast(broadcast)

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

    def __init__(self):
        self.players = []
        self.dealer = 0  # The index of `self.players` who becomes the dealer of the current deal.

        self.sb_amount = 25  # Small blinds amount. Big blinds = 2 * Small blinds.
        self.game_in_progress = False

        self.deal: Deal or None = None

    def start_game(self):
        self.new_deal(cycle_dealer=False)

    def new_deal(self, cycle_dealer=True):
        """
        Start a new deal. Players who are out of money are removed, and the dealer is cycled to the next player.

        :param cycle_dealer: Defaults to True. If set to True then the dealer is cycled to the next player.
        :return: True if a new deal is started; False otherwise, due to insufficient player count.
        """

        self.eliminate_players()
        self.update_player_numbers()

        if cycle_dealer:
            self.dealer = (self.dealer + 1) % len(self.players)  # Cycle dealer

        if len(self.players) >= 2:
            self.deal = Deal(self)
            self.broadcast(GameEvent(GameEvent.NEW_DEAL))
            self.game_in_progress = True
            return True
        else:
            self.game_in_progress = False
            return False

    def eliminate_players(self) -> bool:
        """
        Check the players' amount of money and remove any players that are bankrupt.

        :return: True if at least 1 player was eliminated, otherwise False.
        """
        bankrupt = [player for player in self.players if player.money <= 0]
        self.players = [player for player in self.players if player.money > 0]

        for x in bankrupt:
            x.player_number = -2

        if len(bankrupt) > 0:
            self.update_player_numbers()

        return len(bankrupt) > 0

    def update_player_numbers(self):
        for i, player in enumerate(self.players):
            player.player_number = i

    def on_event(self, event):
        """
        A hook method that is called everytime a game event is broadcasted.
        """
        pass

    def broadcast(self, broadcast: GameEvent) -> None:
        """
        Broadcast a `GameEvent` to all `Player` objects by calling their `receive_event` methods.
        """
        self.on_event(broadcast)

        for player in self.players:
            player.receive_event(broadcast)

    @property
    def min_bet(self):
        return 2 * self.sb_amount
