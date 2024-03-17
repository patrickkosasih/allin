"""
rules/singleplayer.py

The singleplayer module is used to interface the game flow engine from the main app on singleplayer games.
"""


from typing import Callable
import random

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
    def receive_event(self, event: GameEvent):
        # Run self.action after 0.5 seconds
        if event.next_player == self.game.players.index(self):
            app_timer.Timer(0.5, self.decide_action, (event,))

    def decide_action(self, event):
        """
        A low level AI that makes a decision based on only random numbers and the bet amount.
        """

        x = random.randrange(100)
        y = random.randrange(100)

        # all in testing stuff
        # if self.name == "Bot 3":
        #     self.action(Actions.RAISE, 1000)

        if x < 25:
            bet_result = self.action(Actions.RAISE, self.player_hand.bet_amount + 25 * random.randint(1, 4))

            if bet_result:  # If bet not successful
                self.action(Actions.CALL)

        elif x == 69 and 9 < y <= 69:
            self.action(Actions.RAISE, 72727272727)

        else:
            if event.bet_amount > 0:
                if y < 5000 / event.bet_amount:
                    self.action(Actions.CALL)
                else:
                    self.action(Actions.FOLD)

            else:
                self.action(Actions.CALL)


class SingleplayerGame(PokerGame):
    def __init__(self, n_bots: int, starting_money: int, sb_amount: int):
        super().__init__()

        self.the_player = ThePlayer(self, "YOU", starting_money)

        self.bots = [Bot(self, f"Bot {i + 1}", starting_money) for i in range(n_bots)]
        self.players: list[Player] = [self.the_player] + self.bots

        self.sb_amount = sb_amount

