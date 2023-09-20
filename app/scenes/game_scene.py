import pygame
from typing import Optional

from app.widgets.bet_prompt import BetPrompt
from rules.game_flow import GameEvent
import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import widgets
from app import app_timer

from app.animations.move import MoveAnimation
from app.animations.var_slider import VarSlider


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


## noinspection PyUnresolvedReferences,PyTypeChecker
class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.game = rules.singleplayer.SingleplayerGame(6, self.receive_event)

        """
        Miscellaneous GUI
        """
        self.fps_counter = widgets.fps_counter.FPSCounter()
        self.all_sprites.add(self.fps_counter)

        self.flash_fac = 0

        """
        Table and players
        """
        self.table = widgets.table.Table(percent_to_px(50, 50), percent_to_px(55, 55))
        self.all_sprites.add(self.table)

        self.players = pygame.sprite.Group()
        self.reset_players()

        self.winner_crowns = pygame.sprite.Group()

        """
        Table texts
        """
        self.pot_text = widgets.table_texts.PotText(percent_to_px(50, 37.5), percent_to_px(12.5, 5))
        self.all_sprites.add(self.pot_text)
        self.pot_text.set_visible(False, duration=0)

        self.ranking_text = widgets.table_texts.RankingText(percent_to_px(50, 62.5), percent_to_px(17.5, 5))
        self.all_sprites.add(self.ranking_text)
        self.ranking_text.set_visible(False, duration=0)

        """
        Action buttons and bet prompt
        """
        self.action_buttons = pygame.sprite.Group()

        self.fold_button = None
        self.call_button = None
        self.raise_button = None

        self.bet_prompt: Optional[BetPrompt] = None

        self.init_action_buttons()

        """
        Cards and game initialization
        """
        self.game.new_deal(cycle_dealer=False)

        widgets.card.Card.set_size(height=h_percent_to_px(12.5))  # Initialize card size
        self.community_cards = pygame.sprite.Group()

        app_timer.Timer(2, self.deal_cards)
        app_timer.Timer(3, self.pot_text.set_visible, (True,))
        app_timer.Timer(4, self.game.deal.start_deal)

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

            if event.bet_amount > 0 and event.message != "fold":
                action_str += f" ${event.bet_amount:,}"
                self.pot_text.set_text_anim(self.game.deal.pot)

            self.players.sprites()[event.prev_player].set_sub_text_anim(action_str)
            self.players.sprites()[event.prev_player].update_money()

        """
        Show/hide action buttons
        """
        if event.next_player == self.game.players.index(self.game.the_player):
            for x in self.action_buttons:
                x.update_bet_amount(self.game.deal.bet_amount)
            self.show_action_buttons(True)

        elif event.prev_player == self.game.players.index(self.game.the_player):
            self.show_action_buttons(False)

        """
        Round finish and deal end
        """
        match event.code:
            case GameEvent.ROUND_FINISH:
                app_timer.Timer(1, self.game.deal.next_round)

            case GameEvent.NEW_ROUND:
                self.next_round()

            case GameEvent.SKIP_ROUND:
                self.next_round(skip_round=True)

            case GameEvent.DEAL_END:
                app_timer.Timer(1, self.showdown)

    def reset_players(self):
        """
        Initialize or rearrange all the player displays. When calling this function, 3 different scenarios can happen
        for each player display:

        1. Move an existing player display
        2. Create a new player display
        3. Remove an existing player display
        """

        old_group = self.players.copy()
        self.players.empty()

        player_display_datas = [x.player_data for x in old_group.sprites()]
        """A list of the player data of each player display that exists before rearranging the players."""

        for i, player_data in enumerate(self.game.players):
            rot = player_rotation(i, len(self.game.players))
            pos = self.table.get_edge_coords(rot, (1.25, 1.2))

            player_display: widgets.player_display.PlayerDisplay

            if player_data in player_display_datas:
                """
                1. Move player display
                """
                old_i = player_display_datas.index(player_data)
                player_display = old_group.sprites()[old_i]

                # FIXME: There's a bug where the player display disappears after getting moved/rearranged.
                # A thing I noticed is that the player display that disappears is somehow always the last on the list.

            else:
                """
                2. New player display
                """
                start_pos = self.table.get_edge_coords(rot, (3, 3))

                player_display = widgets.player_display.PlayerDisplay(start_pos, percent_to_px(15, 12.5), player_data)
                self.all_sprites.add(player_display)

            self.players.add(player_display)

            animation = MoveAnimation(1.5, player_display, None, pos)
            self.anim_group.add(animation)

        for i, old_player_display in enumerate(old_group.sprites()):
            if old_player_display not in self.players:
                """
                3. Remove player display
                """
                print(f"{old_player_display.player_data.name} removed")

                rot = player_rotation(i, len(old_group))
                pos = self.table.get_edge_coords(rot, (3, 3))

                animation = MoveAnimation(1.5, old_player_display, None, pos,
                                          call_on_finish=lambda: self.all_sprites.remove(old_player_display))
                self.anim_group.add(animation)

    def init_action_buttons(self):
        """
        Initialize the three action buttons and the bet prompt.
        """

        """
        Measurements
        """
        dimensions = w, h = percent_to_px(15, 6.5)  # Button dimensions
        w_scr, h_scr = pygame.display.get_window_size()  # Window dimensions
        m = h / 3  # Margin between button and the edges (bottom and right).

        x, y = w_scr - w / 2 - m, h_scr - h / 2 - m  # First button position
        y_list = [y - i * (h + m) for i in range(3)]  # List of y positions

        positions = [(x, y) for y in y_list]  # List of all button positions

        """
        Action buttons
        """
        self.fold_button = widgets.action_buttons.FoldButton(positions[0], dimensions, self.game.the_player)
        self.call_button = widgets.action_buttons.CallButton(positions[1], dimensions, self.game.the_player)
        self.raise_button = widgets.action_buttons.RaiseButton(positions[2], dimensions, self.game.the_player, self)

        for x in (self.fold_button, self.call_button, self.raise_button):
            self.action_buttons.add(x)
            self.all_sprites.add(x)
            x.set_shown(False, 0.0)

        """
        Bet prompt
        """
        wbp, hbp = w_percent_to_px(30), 2 * h + m  # Width and height of bet prompt

        self.bet_prompt = BetPrompt((w_scr - wbp/2 - m, h_scr - hbp/2 - m),
                                    (wbp, hbp), self, self.game.the_player)
        self.all_sprites.add(self.bet_prompt)
        self.bet_prompt.set_shown(False, 0.0)

    def show_action_buttons(self, shown: bool):
        for i, x in enumerate(self.action_buttons):
            x.set_shown(shown, duration=0.4 + 0.05 * i)

    def show_bet_prompt(self, shown: bool):
        self.bet_prompt.set_shown(shown)

        for x in (self.call_button, self.fold_button):
            x.set_shown(not shown, duration=0.3)

    def deal_cards(self):
        for i, player_display in enumerate(self.players.sprites()):
            for j in range(2):  # Every player has 2 pocket cards
                x, y = player_display.rect.midtop
                x += w_percent_to_px(1) * (1 if j else -1)

                angle = player_rotation(i, len(self.players.sprites())) + random.uniform(-2, 2)
                start_pos = self.table.get_edge_coords(angle, (2.75, 2.75))

                card = widgets.card.Card(start_pos)
                animation = MoveAnimation(random.uniform(1.75, 2), card, None, (x, y))
                self.anim_group.add(animation)

                # Pocket cards are added to 2 different sprite groups.
                self.all_sprites.add(card)
                player_display.pocket_cards.add(card)

                if player_display.player_data is self.game.the_player:
                    card.card_data = player_display.player_data.player_hand.pocket_cards[j]
                    animation.call_on_finish = card.reveal

    def next_round(self, skip_round=False):
        """
        The method that is called when the deal advances to the next round (a NEW_ROUND game event is received).

        :param skip_round:
        """

        if self.game.deal.winners:
            return

        for player in self.players.sprites():
            player.set_sub_text_anim("")

        for i in range(len(self.community_cards), len(self.game.deal.community_cards)):
            card_data = self.game.deal.community_cards[i]

            start_pos = self.table.get_edge_coords(COMM_CARD_ROTATIONS[i] + random.uniform(-5, 5), (3, 3))
            pos = percent_to_px(50 + 6.5 * (i - 2), 50)

            card = widgets.card.Card(start_pos, card_data)
            # card.show_front()

            animation = MoveAnimation(2 + i / 8, card, start_pos, pos, call_on_finish=card.reveal)
            self.anim_group.add(animation)

            self.all_sprites.add(card)
            self.community_cards.add(card)

        anim_delay = 2 + len(self.community_cards) / 8
        ranking_int = self.game.the_player.player_hand.hand_ranking.ranking_type
        ranking_str = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()

        app_timer.Timer(anim_delay, self.ranking_text.set_text_anim, (ranking_str,))

        if len(self.game.deal.community_cards) == 3:
            app_timer.Timer(2, self.ranking_text.set_visible, (True,))

        if skip_round:
            app_timer.Timer(anim_delay, self.game.deal.next_round)  # Skip round
        else:
            app_timer.Timer(anim_delay + 0.25, self.game.deal.start_new_round)  # Start new round

    def showdown(self):
        """
        Perform a showdown and reveal the winner(s) of the current deal.
        """

        self.ranking_text.set_visible(False)
        for player in self.players.sprites():
            player.set_sub_text_anim("")

        """
        Show all pocket cards
        """
        for player_display in self.players.sprites():
            if player_display.player_data is not self.game.the_player:
                for i, card in enumerate(player_display.pocket_cards.sprites()):
                    card.card_data = player_display.player_data.player_hand.pocket_cards[i]
                    card.reveal(random.uniform(1, 1.5))

        """
        Get a sorted list of player indexes sorted from the lowest hand ranking to the winners.
        """
        get_score = lambda x: x[1].player_data.player_hand.hand_ranking.overall_score
        # A lambda function that gets the player's overall score of an (index, player display) tuple.

        is_not_folded = lambda x: not x.player_data.player_hand.folded
        # A lambda function that returns True if the player (`x: PlayerDisplay`) is not folded.

        sorted_players = [i for i, player in sorted(enumerate(self.players), key=get_score) if is_not_folded(player)]
        # A list of player indexes who hasn't folded sorted by the hand ranking.

        """
        Start revealing the hand rankings
        """
        app_timer.Timer(2, self.reveal_rankings, args=(sorted_players,))

        """
        Start a new deal in 8 seconds
        """
        app_timer.Timer(8, self.new_deal)

    def reveal_rankings(self, sorted_players, i=0):
        """
        Reveal the hand rankings of each player one by one in order from the lowest ranking.

        :param sorted_players: The list of player indexes sorted by the hand ranking.
        :param i: The index of sorted_players to show. This method recursively calls itself (using a timer with a delay)
        with `i + 1` as the new argument.
        """
        if i >= len(sorted_players):
            """
            Flash the screen and set the pot text to 0 when revealing the winner
            """
            def set_flash_fac(flash_fac):
                self.flash_fac = int(flash_fac)

            animation = VarSlider(1.5, 50, 0, setter_func=set_flash_fac)
            self.anim_group.add(animation)

            self.pot_text.set_text_anim(0)

            return

        player_display = self.players.sprites()[sorted_players[i]]
        player_hand = player_display.player_data.player_hand

        # Update sub text to hand ranking
        ranking_int = player_hand.hand_ranking.ranking_type
        ranking_text = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()
        player_display.set_sub_text_anim(ranking_text)



        if player_hand in self.game.deal.winners:
            """
            Reveal the winner
            """
            # Create a winner crown
            winner_crown = widgets.winner_crown.WinnerCrown(player_display)
            self.all_sprites.add(winner_crown)
            self.winner_crowns.add(winner_crown)

            # Update player money text
            player_display.update_money()

            # Call `reveal_rankings` again without delay to reveal other winners if there are any.
            # Calling the function when the new `i` is out of range creates the screen flash effect.
            self.reveal_rankings(sorted_players, i + 1)

        else:
            next_player_delay = 1 / (len(sorted_players) - len(self.game.deal.winners) - i + 1)
            app_timer.Timer(next_player_delay, self.reveal_rankings, args=(sorted_players, i + 1))

    def new_deal(self):
        """
        Reset the sprites of cards and winner crowns, and then start a new deal.
        """

        self.pot_text.set_visible(False)
        self.ranking_text.set_text("")

        """
        Clear winner crowns
        """
        for winner_crown in self.winner_crowns.sprites():
            winner_crown.hide()

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

        app_timer.Timer(2.5, self.delete_on_new_deal)

        """
        Call the new deal method
        """
        is_new_deal = self.game.new_deal()

        """
        Rearrange players if the players list has changed
        """
        if len(self.players.sprites()) != len(self.game.players) or \
            any(x.player_data is not y for x, y in zip(self.players.sprites(), self.game.players)):

            app_timer.Timer(2.5, self.reset_players)
            rearrange_delay = 1.5

        else:
            rearrange_delay = 0

        """
        Reset action buttons
        """
        for x in (self.fold_button, self.call_button, self.raise_button):
            x.set_shown(False, 0.0)

        self.call_button.all_in = False

        """
        Start a new deal after a delay
        """
        if is_new_deal:
            app_timer.Timer(3 + rearrange_delay, self.deal_cards)
            app_timer.Timer(4 + rearrange_delay, self.pot_text.set_visible, (True,))
            app_timer.Timer(5 + rearrange_delay, self.game.deal.start_deal)

    def delete_on_new_deal(self):
        """
        When starting a new deal, remove all pocket cards, community cards, and winner crowns from the `all_sprites`
        sprite group and other sprite groups.
        """

        for player in self.players.sprites():
            for card in player.pocket_cards.sprites():
                self.all_sprites.remove(card)

            player.pocket_cards.empty()

        for sprite in self.community_cards.sprites() + self.winner_crowns.sprites():
            self.all_sprites.remove(sprite)

        self.community_cards.empty()
        self.winner_crowns.empty()

    def update(self, dt):
        super().update(dt)

        if self.flash_fac > 0:
            self.display_surface.fill(3 * (self.flash_fac,), special_flags=pygame.BLEND_RGB_ADD)
