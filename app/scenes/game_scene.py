import pygame.sprite
import threading
import tkinter.simpledialog

from rules.game_flow import ActionResult
import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import widgets
from app import app_timer


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

        self.winner_crowns = pygame.sprite.Group()

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
        self.all_pocket_cards = pygame.sprite.Group()
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
        # print("Your turn")
        pass

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

                # Pocket cards are added to 3 different sprite groups.
                self.all_sprites.add(card)
                self.all_pocket_cards.add(card)
                player_display.pocket_cards.add(card)

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
            player_hand = player_display.player_data.player_hand

            # Update sub text to hand ranking
            ranking_int = player_hand.hand_ranking.ranking_type
            ranking_text = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()
            player_display.set_sub_text(ranking_text)

            # Update money text
            player_display.update_money()

            # Show cards
            for i, card in enumerate(player_display.pocket_cards.sprites()):
                card.card_data = player_hand.pocket_cards[i]
                card.show_front()

            # If the player is a winner, create a winner crown.
            if player_hand in self.game.deal.winners:
                winner_crown = widgets.winner_crown.WinnerCrown(player_display)
                self.all_sprites.add(winner_crown)
                self.winner_crowns.add(winner_crown)

        app_timer.Timer(4, self.new_deal)

    def new_deal(self):
        """
        Reset the sprites of cards and winner crowns, and then start a new deal.
        """

        """
        Clear cards and winner crowns
        """
        reset_sprites = self.all_pocket_cards.sprites() + self.community_cards.sprites() + self.winner_crowns.sprites()

        # Remove sprites from the all_sprites group
        for sprite in reset_sprites:
            self.all_sprites.remove(sprite)

        # Empty the `pocket_cards` groups and reset sub texts of every player
        for player in self.players:
            player.pocket_cards.empty()
            player.set_sub_text("")

        # Empty sprite groups
        self.all_pocket_cards.empty()
        self.community_cards.empty()
        self.winner_crowns.empty()

        """
        New deal
        """
        self.game.new_deal()

        if len(self.players.sprites()) != len(self.game.players):
            for player in self.players.sprites():
                self.all_sprites.remove(player)

            self.players.empty()
            self.init_players()

        self.deal_cards()

    def update(self, dt):
        super().update(dt)
