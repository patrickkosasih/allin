import pygame.sprite
import threading
import tkinter.simpledialog
import random

from app.animations.move import MoveAnimation
from rules.game_flow import GameEvent
import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import widgets
from app import app_timer


COMM_CARD_ROTATIONS = (198, 126, 270, 54, -18)
"""`COMM_CARD_ROTATIONS` defines the rotation for the animation's starting position of the n-th community card."""


def player_rotation(i: int, n_players: int) -> float:
    """
    Returns the player rotation for the given player index and number of players.

    A player rotation defines the position of a player display in the table. The returned player rotation is usually
    converted into a (x, y) position using the `Table.get_edge_coords` method.

    :param i: The index of the player.
    :param n_players: Total number of players.
    :return: The player rotation in degrees.
    """
    return i * (360 / n_players) + 90


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.game = rules.singleplayer.SingleplayerGame(6, self.receive_event)

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
        self.community_cards = pygame.sprite.Group()

        self.deal_cards()
        app_timer.Timer(2, self.game.deal.start_deal)


    def receive_event(self, event: GameEvent):
        """
        The method that is called everytime an action or event happens.
        """
        # print(event)

        """
        Update the subtext on a player action
        """
        if event.prev_player >= 0:
            action_str = event.message.capitalize()

            if event.bet_amount > 0:
                action_str += f" ${event.bet_amount:,}"

            self.players.sprites()[event.prev_player].set_sub_text_anim(action_str)
            self.players.sprites()[event.prev_player].update_money()

        """
        Round finish and deal end
        """
        match event.code:
            case GameEvent.ROUND_FINISH | GameEvent.SKIP_ROUND:
                app_timer.Timer(1, self.next_round)

            case GameEvent.DEAL_END:
                app_timer.Timer(1.5, self.showdown)

    def init_players(self):
        for i, player_data in enumerate(self.game.players):
            player_display = widgets.player_display.PlayerDisplay(
                self.table.get_edge_coords(player_rotation(i, len(self.game.players)), (1.25, 1.2)),
                percent_to_px(15, 12.5),
                player_data
            )
            self.players.add(player_display)
            self.all_sprites.add(player_display)

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

        if action_type in ("RAISE", "BET"):
            # Raising and betting is currently done by inputting the new betting amount to the command line.
            # In the future, a slider GUI for betting will be implemented.
            def prompt():
                new_amount = tkinter.simpledialog.askinteger("Bet / Raise", "Input new betting amount")
                if not new_amount:
                    return

                self.game.the_player.action(rules.game_flow.Actions.RAISE, new_amount)

            threading.Thread(target=prompt, daemon=True).start()

        if action_type not in rules.game_flow.Actions.__dict__:
            raise ValueError(f"invalid action: {action_type}")

        self.game.the_player.action(rules.game_flow.Actions.__dict__[action_type])

    def deal_cards(self):
        for i, player_display in enumerate(self.players.sprites()):
            for j in range(2):  # Every player has 2 pocket cards
                x, y = player_display.rect.midtop
                x += w_percent_to_px(1) * (1 if j else -1)

                angle = player_rotation(i, len(self.players.sprites())) + random.uniform(-2, 2)
                start_pos = self.table.get_edge_coords(angle, (2.5, 2.5))

                card = widgets.card.Card(start_pos)
                animation = MoveAnimation(random.uniform(1.75, 2), card, None, (x, y))
                self.anim_group.add(animation)

                # Pocket cards are added to 2 different sprite groups.
                self.all_sprites.add(card)
                player_display.pocket_cards.add(card)

                if player_display.player_data is self.game.the_player:
                    card.card_data = player_display.player_data.player_hand.pocket_cards[j]
                    animation.call_on_finish = card.reveal

    def next_round(self):
        for player in self.players.sprites():
            player.set_sub_text_anim("")

        self.game.deal.next_round()

        for i in range(len(self.community_cards), len(self.game.deal.community_cards)):
            card_data = self.game.deal.community_cards[i]

            start_pos = self.table.get_edge_coords(COMM_CARD_ROTATIONS[i] + random.uniform(-5, 5), (3, 3))
            pos = percent_to_px(50 + 6.5 * (i - 2), 50)

            card = widgets.card.Card(start_pos, card_data)
            # card.show_front()

            animation = MoveAnimation(random.uniform(2, 2.5), card, start_pos, pos, call_on_finish=card.reveal)
            self.anim_group.add(animation)

            self.all_sprites.add(card)
            self.community_cards.add(card)

    def showdown(self):
        for player_display in self.players.sprites():
            player_hand = player_display.player_data.player_hand

            # Update sub text to hand ranking
            ranking_int = player_hand.hand_ranking.ranking_type
            ranking_text = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()
            player_display.set_sub_text_anim(ranking_text)

            # Update money text
            player_display.update_money()

            # Show cards
            if player_display.player_data is not self.game.the_player:
                for i, card in enumerate(player_display.pocket_cards.sprites()):
                    card.card_data = player_hand.pocket_cards[i]
                    card.reveal(random.uniform(0.5, 1))

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
        Delete winner crowns
        """
        for sprite in self.winner_crowns.sprites():
            self.all_sprites.remove(sprite)

        self.winner_crowns.empty()

        """
        Clear cards
        """
        # Pocket cards
        for i, player in enumerate(self.players.sprites()):
            for card in player.pocket_cards.sprites():
                # self.all_sprites.remove(card)
                card_end_pos = self.table.get_edge_coords(
                    player_rotation(i, len(self.players.sprites())) + random.uniform(-2, 2), (3, 3)
                )
                animation = MoveAnimation(random.uniform(1.5, 2), card, None, card_end_pos)
                self.anim_group.add(animation)

            player.set_sub_text_anim("")  # Reset sub text

        # Community cards
        for card, rot in zip(self.community_cards.sprites(), COMM_CARD_ROTATIONS):
            card_end_pos = self.table.get_edge_coords(rot + random.uniform(-5, 5), (3, 3))
            animation = MoveAnimation(random.uniform(2, 2.5), card, None, card_end_pos)
            self.anim_group.add(animation)

        app_timer.Timer(2.5, self.delete_cards)

        """
        New deal
        """
        is_new_deal = self.game.new_deal()

        if len(self.players.sprites()) != len(self.game.players):
            for player in self.players.sprites():
                self.all_sprites.remove(player)

            self.players.empty()
            self.init_players()

        if is_new_deal:
            app_timer.Timer(3, self.deal_cards)
            app_timer.Timer(5, self.game.deal.start_deal)

    def delete_cards(self):
        for player in self.players.sprites():
            for card in player.pocket_cards.sprites():
                self.all_sprites.remove(card)

            player.pocket_cards.empty()

        for card in self.community_cards:
            self.all_sprites.remove(card)

        self.community_cards.empty()

    def update(self, dt):
        super().update(dt)
