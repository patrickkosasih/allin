"""
rules/singleplayer.py

The singleplayer module is used to interface the game flow engine from the main app on singleplayer games.
"""

from app.tools import app_timer
from rules.game_flow import *
from rules.interface import *


class Bot(Player):
    def receive_event(self, event: GameEvent):
        # Run self.action after 0.5 seconds
        if event.next_player == self.game.players.index(self):
            self.game: SingleplayerGame
            timer_group = self.game.timer_group if type(self.game) is SingleplayerGame else None

            app_timer.Timer(0.5, self.decide_action, (event,), group=timer_group)

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


class SingleplayerGame(InterfaceGame):
    """
    The `SingleplayerGame` class is the rules engine for local singleplayer games. The `SingleplayerGame` child class
    also handles the timing/delay of events, e.g. after a round ends, the game waits for a moment to start the next
    round.
    """

    def __init__(self, n_bots: int, starting_money: int, sb_amount: int):
        super().__init__()

        self.client_player = ClientPlayer(self, "YOU", starting_money)
        self.bots = [Bot(self, f"Bot {i + 1}", starting_money) for i in range(n_bots)]
        self.players: list[Player] = [self.client_player] + self.bots

        self.sb_amount = sb_amount

    def on_event(self, event):
        self.event_receiver(event)
        self.time_next_event(event)

    def start_game(self):
        self.broadcast(GameEvent(GameEvent.RESET_PLAYERS))
        self.timer_group.new_timer(2, self.new_deal, (False,))

    def time_next_event(self, event):
        match event.code:
            case GameEvent.RESET_PLAYERS:
                pass
                # self.timer_group.new_timer(2, self.new_deal, (self.game_in_progress,))

            case GameEvent.NEW_DEAL:
                self.timer_group.new_timer(2, self.deal.start_deal)

            case GameEvent.ROUND_FINISH:
                self.timer_group.new_timer(1, self.deal.next_round)

            case GameEvent.NEW_ROUND:
                self.timer_group.new_timer(2.25 + len(self.deal.community_cards) / 8, self.deal.start_new_round)

            case GameEvent.SKIP_ROUND:
                self.timer_group.new_timer(2.25 + len(self.deal.community_cards) / 8, self.deal.next_round)

            case GameEvent.DEAL_END:
                self.timer_group.new_timer(10, self.broadcast, (GameEvent(GameEvent.RESET_DEAL),))

            case GameEvent.RESET_DEAL:
                reset_players = self.eliminate_players()

                if reset_players:
                    self.timer_group.new_timer(2.5, self.broadcast, (GameEvent(GameEvent.RESET_PLAYERS),))
                    self.timer_group.new_timer(4.5, self.new_deal)

                else:
                    self.timer_group.new_timer(3, self.new_deal)
