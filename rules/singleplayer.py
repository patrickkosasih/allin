from typing import Callable
from app import app_timer

from rules.game_flow import *


class ThePlayer(Player):
    def __init__(self, game: "SingleplayerGame", name: str, money: int):
        super().__init__(game, name, money)
        self.game = game

    def on_any_action(self, action_result: ActionResult):
        """
        Calls every time any player makes an action.
        """
        self.game.call_on_any_action(action_result)

    def on_turn(self):
        """
        Calls when the new turn after an action is this player.
        """
        self.game.call_on_turn()


class Bot(Player):
    def on_turn(self):
        # Run self.action after 0.5 seconds
        app_timer.Timer(0.5, self.action, (Actions.CALL,))


class SingleplayerGame(PokerGame):
    def __init__(self, n_players: int,
                 call_on_any_action: Callable[[ActionResult], None], call_on_turn: Callable[[None], None],
                 auto_start=False):
        super().__init__()

        self.the_player = ThePlayer(self, "YOU", 1000)

        self.bots = [Bot(self, f"Bot {i + 1}", 1000) for i in range(n_players - 1)]
        self.players: list[Player] = [self.the_player] + self.bots

        self.call_on_any_action = call_on_any_action
        self.call_on_turn = call_on_turn

        if auto_start:
            self.new_deal()

