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

        self.game = rules.singleplayer.SingleplayerGame(8, self.on_any_action, self.on_turn)

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
        Testing stuff
        """
        self.cards = pygame.sprite.Group()
        deck_iter = iter(self.game.deal.deck)

        for i in range(-2, 3):
            card = widgets.card.Card(percent_to_px(50 + 6.5 * i, 50), h_percent_to_px(12.5), next(deck_iter))
            self.cards.add(card)
            self.all_sprites.add(card)

        # self.thing = widgets.button.Button(percent_to_px(50, 50), percent_to_px(15, 7.5), text="Hi",
        #                                    command=lambda: print("Hello, World!"), b_thickness=5)
        # self.all_sprites.add(self.thing)


    def on_any_action(self, action_result: ActionResult):
        if action_result.code == ActionResult.NEW_ROUND:
            for player in self.players.sprites():
                player.set_sub_text("")

        else:
            action_str = action_result.message.capitalize()
            if action_result.bet_amount > 0:
                action_str += f" ${action_result.bet_amount:,}"

            self.players.sprites()[action_result.player_index].set_sub_text(action_str)

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
        pass

    def update(self):
        super().update()
