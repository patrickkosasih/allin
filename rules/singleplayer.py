"""
rules/singleplayer.py

The singleplayer module is used to interface the game flow engine from the main app on singleplayer games.
"""


from typing import Callable
from app import app_timer

from rules.game_flow import *


class ThePlayer(Player):
    def __init__(self, game: "SingleplayerGame", name: str, money: int):
        super().__init__(game, name, money)
        self.game = game

    def receive_event(self, game_event: GameEvent):
        """
        Calls every time any player makes an action.
        """
        self.game.call_on_any_action(game_event)


class Bot(Player):
    def receive_event(self, broadcast: GameEvent):
        # Run self.action after 0.5 seconds
        if broadcast.next_player == self.game.players.index(self):
            app_timer.Timer(0.5, self.action, (Actions.CALL,))


class SingleplayerGame(PokerGame):
    def __init__(self, n_players: int,
                 call_on_any_action: Callable[[GameEvent], None],
                 auto_start=False):
        super().__init__()

        self.the_player = ThePlayer(self, "YOU", 1000)

        self.bots = [Bot(self, f"Bot {i + 1}", 1000) for i in range(n_players - 1)]
        self.players: list[Player] = [self.the_player] + self.bots

        self.call_on_any_action = call_on_any_action

        if auto_start:
            self.new_deal()

