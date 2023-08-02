import pygame.sprite

import tkinter.simpledialog

from rules.game_flow import ActionResult
import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import widgets


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.game = rules.singleplayer.SingleplayerGame(6, self.on_any_action, self.on_turn)

        self.fps_counter = widgets.fps_counter.FPSCounter()
        self.all_sprites.add(self.fps_counter)

        widgets.card.Card.set_size(height=h_percent_to_px(12.5))  # Initialize card size

        """
        Table and players
        """
        self.table = widgets.table.Table(percent_to_px(50, 50), percent_to_px(55, 55))
        self.all_sprites.add(self.table)

        self.players = pygame.sprite.Group()
        self.init_players()

        """
        Action buttons
        """
        self.action_buttons = {
            "fold": None,
            "call": None,
            "raise": None
        }
        self.init_action_buttons()

        self.game.new_deal(cycle_dealer=False)

        """
        Cards
        """
        self.pocket_cards = pygame.sprite.Group()
        self.community_cards = pygame.sprite.Group()

        self.deal_cards()


    def on_any_action(self, action_result: ActionResult):
        if action_result.code == ActionResult.NEW_ROUND:
            self.next_round()

        elif action_result.code == ActionResult.DEAL_END:
            self.showdown()

        else:
            action_str = action_result.message.capitalize()
            if action_result.bet_amount > 0:
                action_str += f" ${action_result.bet_amount:,}"

            self.players.sprites()[action_result.player_index].set_sub_text(action_str)

        self.players.sprites()[action_result.player_index].update_money()

    def on_turn(self):
        print("Your turn")

    def init_players(self):
        player_angle = 360 / len(self.game.players)  # The angle between players in degrees

        for i, player_data in enumerate(self.game.players):
            player = widgets.player_display.PlayerDisplay(self.table.get_edge_coords(i * player_angle + 90, (1.25, 1.2)),
                                                          percent_to_px(15, 12.5),
                                                          player_data)
            self.players.add(player)
            self.all_sprites.add(player)

    def init_action_buttons(self):
        """
        Initialize the three action buttons.
        """
        colors = {
            "fold": (184, 51, 51),
            "call": (24, 142, 163),
            "raise": (168, 149, 24)
        }

        """
        Measurements
        """
        w, h = percent_to_px(15, 6.5)  # Button dimensions
        w_scr, h_scr = pygame.display.get_window_size()  # Window dimensions
        m = h / 3  # Margin between button and the edges (bottom and right).
        x, y = w_scr - w / 2 - m, h_scr - h / 2 - m  # First button position

        for action in self.action_buttons.keys():
            button = widgets.button.Button(pos=(x, y), dimensions=(w, h), color=colors[action],
                                           command=lambda a=action: self.action_button_press(a),
                                           text=action.capitalize(), text_color="white")

            self.action_buttons[action] = button
            self.all_sprites.add(button)

            y -= h + m

    def action_button_press(self, action_type: str):
        action_type = action_type.upper()
        new_amount = 0

        if action_type in ("RAISE", "BET"):
            # Raising and betting is currently done by inputting the new betting amount to the command line.
            # In the future, a slider GUI for betting will be implemented.
            new_amount = tkinter.simpledialog.askinteger("Bet / Raise", "Input new betting amount")

            if not new_amount:
                return

        if action_type not in rules.game_flow.Actions.__dict__:
            raise ValueError(f"invalid action: {action_type}")

        self.game.the_player.action(rules.game_flow.Actions.__dict__[action_type], new_amount)

    def deal_cards(self):
        for player_display in self.players.sprites():
            for i in range(2):  # Every player has 2 pocket cards
                x, y = player_display.rect.midtop
                x += w_percent_to_px(1) * (1 if i else -1)

                card = widgets.card.Card((x, y))
                self.all_sprites.add(card)
                self.pocket_cards.add(card)

                if player_display.player_data is self.game.the_player:
                    card.card_data = player_display.player_data.player_hand.pocket_cards[i]
                    card.show_front()

    def next_round(self):
        for player in self.players.sprites():
            player.set_sub_text("")

        for i in range(len(self.community_cards), len(self.game.deal.community_cards)):
            card_data = self.game.deal.community_cards[i]
            pos = percent_to_px(50 + 6.5 * (i - 2), 50)

            card = widgets.card.Card(pos, card_data)
            card.show_front()

            self.all_sprites.add(card)
            self.community_cards.add(card)

    def showdown(self):
        for player_display in self.players.sprites():
            ranking_int = player_display.player_data.player_hand.hand_ranking.ranking_type
            ranking_text = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()

            player_display.set_sub_text(ranking_text)

    def update(self, dt):
        super().update(dt)
