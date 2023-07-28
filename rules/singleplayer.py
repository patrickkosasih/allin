from rules.game_flow import *
from typing import Callable


class ThePlayer(Player):
    def __init__(self, game: "SingleplayerGame", name: str, money: int):
        super().__init__(game, name, money)
        self.game = game

    def on_any_action(self, action_result: ActionResult):
        """
        Calls every time any player makes an action.
        """
        self.game.call_on_any_action()

    def on_turn(self):
        """
        Calls when the new turn after an action is this player.
        """
        self.game.call_on_turn()


class Bot(Player):
    def on_turn(self):
        self.action(Actions.CALL)


class SingleplayerGame(PokerGame):
    def __init__(self, n_players: int,
                 call_on_any_action: Callable, call_on_turn: Callable):
        super().__init__()

        self.the_player = ThePlayer(self, "YOU", 1000)

        self.bots = [Bot(self, f"Bot {i + 1}", 1000) for i in range(n_players - 1)]
        self.players: list[Player] = [self.the_player] + self.bots

        self.call_on_any_action = call_on_any_action
        self.call_on_turn = call_on_turn

        self.new_deal()

