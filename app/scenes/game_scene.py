import pygame

from rules.game_flow import GameEvent
import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import app_timer

from app import widgets
from app.widgets.game.card import Card
from app.widgets.game.action_buttons import FoldButton, RaiseButton, CallButton
from app.widgets.game.dealer_button import DealerButton
from app.widgets.game.winner_crown import WinnerCrown
from app.widgets.game.player_display import PlayerDisplay
from app.widgets.game.bet_prompt import BetPrompt
from app.widgets.basic.fps_counter import FPSCounter

from app.animations.move import MoveAnimation
from app.animations.var_slider import VarSlider
from app.animations.fade import FadeAlpha


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
    def __init__(self, app):
        super().__init__(app)

        self.game = rules.singleplayer.SingleplayerGame(6, self.receive_event)

        """
        Miscellaneous GUI
        """
        self.fps_counter = FPSCounter(self, 0.5, 0.5, 15, 5, "%", "tl", "tl")
        self.all_sprites.add(self.fps_counter)

        self.flash_fac = 0

        """
        Table and players
        """
        self.table = widgets.game.table.Table(self, 0, 0, 55, 55, "%", "ctr", "ctr")

        self.players = pygame.sprite.Group()
        self.winner_crowns = pygame.sprite.Group()

        """
        Table texts
        """
        self.pot_text = widgets.game.table_texts.PotText(self, 0, -12.5, 12.5, 5, "%", "ctr", "ctr")
        self.pot_text.set_visible(False, duration=0)

        self.ranking_text = widgets.game.table_texts.RankingText(self, 0, 12.5, 17.5, 5, "%", "ctr", "ctr")
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
        Dealer and blinds buttons
        """
        self.dealer_button = None
        self.sb_button = None
        self.bb_button = None

        """
        Cards and game initialization
        """
        self.game.new_deal(cycle_dealer=False)

        Card.set_size(height=h_percent_to_px(12.5))  # Initialize card size
        self.community_cards = pygame.sprite.Group()

        self.reset_players()

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
        Fold
        """
        if event.message == "fold":
            self.fold_cards(event.prev_player)

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

        self.hide_dealer_button()

        old_group = self.players.copy()
        self.players.empty()

        player_display_datas = [x.player_data for x in old_group.sprites()]
        """A list of the player data of each player display that exists before rearranging the players."""

        for i, player_data in enumerate(self.game.players):
            rot = player_rotation(i, len(self.game.players))
            pos = self.table.get_edge_coords(rot, (1.25, 1.2))

            player_display: PlayerDisplay

            if player_data in player_display_datas:
                """
                1. Move player display
                """
                old_i = player_display_datas.index(player_data)
                player_display = old_group.sprites()[old_i]

            else:
                """
                2. New player display
                """
                start_pos = self.table.get_edge_coords(rot, (3, 3))

                player_display = PlayerDisplay(self, *start_pos, 15, 12.5, "px %", "tl", "ctr",
                                               player_data=player_data)

            self.players.add(player_display)

            player_display.move_anim(1.5, pos)

        for i, old_player_display in enumerate(old_group.sprites()):
            if old_player_display not in self.players:
                """
                3. Remove player display
                """

                rot = player_rotation(i, len(old_group))
                pos = self.table.get_edge_coords(rot, (3, 3))

                old_player_display.move_anim(1.5, pos,
                                             call_on_finish=lambda x=old_player_display: self.all_sprites.remove(x))

    def init_action_buttons(self):
        """
        Initialize the three action buttons and the bet prompt.
        """

        """
        Measurements
        """
        dimensions = w, h = (15, 6.5)  # Button dimensions (in %screen)
        m = 2  # Margin in %screen

        rects = [(-m, (-m - i * (h + m)), w, h, "%", "br", "br") for i in range(3)]  # List of all the button rects

        self.fold_button = FoldButton(self, *rects[0], player=self.game.the_player)
        self.call_button = CallButton(self, *rects[1], player=self.game.the_player)
        self.raise_button = RaiseButton(self, *rects[2], player=self.game.the_player)

        for x in (self.fold_button, self.call_button, self.raise_button):
            self.action_buttons.add(x)
            x.set_shown(False, 0.0)

        """
        Bet prompt
        """
        bp_dimensions = 30, 2 * h + m  # Width and height of bet prompt (in %screen)

        self.bet_prompt = BetPrompt(self, -m, -m, *bp_dimensions, "%", "br", "br",
                                    game_scene=self, player=self.game.the_player)
        self.bet_prompt.set_shown(False, 0.0)

    def show_action_buttons(self, shown: bool):
        for i, x in enumerate(self.action_buttons):
            x.set_shown(shown, duration=0.4 + 0.05 * i)

    def show_bet_prompt(self, shown: bool):
        self.bet_prompt.set_shown(shown)

        for x in (self.call_button, self.fold_button):
            x.set_shown(not shown, duration=0.3)

    def deal_cards(self):
        """
        Deals the pocket cards to all players and also moves the dealer button.
        """
        self.move_dealer_button()

        for i, player_display in enumerate(self.players.sprites()):
            for j in range(2):  # Every player has 2 pocket cards
                x, y = player_display.rect.midtop
                x += w_percent_to_px(1) * (1 if j else -1)

                angle = player_rotation(i, len(self.players.sprites())) + random.uniform(-2, 2)
                start_pos = self.table.get_edge_coords(angle, (2.75, 2.75))

                card = Card(self, *start_pos)
                animation = card.move_anim(random.uniform(1.75, 2), (x, y))

                # Pocket cards are added to 2 different sprite groups.
                self.all_sprites.add(card)
                player_display.pocket_cards.add(card)

                if player_display.player_data is self.game.the_player:
                    card.card_data = player_display.player_data.player_hand.pocket_cards[j]
                    animation.call_on_finish = card.reveal

    def highlight_cards(self, showdown=False, unhighlight=False):
        """
        Select the cards that make up a poker hand and highlight them.

        :param showdown: If True, then highlight the winning hand (the ranked cards and the kickers).
        Otherwise, highlight the ranked cards of the client user player (the kickers are not highlighted).

        :param unhighlight: If set to True then clear all the highlights.
        """

        if showdown:
            # Showdown: Highlight the winning hand(s)
            ranked_cards = set(x for winner in self.game.deal.winners for x in winner.hand_ranking.ranked_cards)
            kickers = set(x for winner in self.game.deal.winners for x in winner.hand_ranking.kickers)
        else:
            # Highlight the ranked cards of "the player" (client user)
            ranked_cards = set(self.game.the_player.player_hand.hand_ranking.ranked_cards)
            kickers = set()

        highlighted_cards = set.union(ranked_cards, kickers)
        card_displays = self.community_cards.sprites() + [card for player_display in self.players
                                                          for card in player_display.pocket_cards]

        for card_display in card_displays:
            if card_display.is_revealed:
                card_display.show_highlight(card_display.card_data in highlighted_cards and not unhighlight,
                                            ranked=card_display.card_data not in kickers)

    def fold_cards(self, i: int):
        """
        Discard the pocket cards of the specified player when that player folds.

        :param i: The index of the player.
        """
        player = self.players.sprites()[i]

        for card in player.pocket_cards:
            if player.player_data is self.game.the_player:
                animation = FadeAlpha(0.25, card, -1, 128)
                self.anim_group.add(animation)

                if self.ranking_text.visible:
                    self.ranking_text.set_text_anim("Folded:  " + self.ranking_text.text_str)

            else:
                angle = player_rotation(i, len(self.players.sprites())) + random.uniform(-2, 2)
                pos = self.table.get_edge_coords(angle, (2.75, 2.75))

                animation = MoveAnimation(random.uniform(1, 1.5), card, None, pos)
                self.anim_group.add(animation)

    def next_round(self, skip_round=False):
        """
        The method that is called when the deal advances to the next round (a NEW_ROUND game event is received).

        :param skip_round:
        """

        if self.game.deal.winners:
            return

        for player in self.players.sprites():
            player.set_sub_text_anim("All in" if player.player_data.player_hand.all_in else "")

        for i in range(len(self.community_cards), len(self.game.deal.community_cards)):
            card_data = self.game.deal.community_cards[i]

            start_pos = self.table.get_edge_coords(COMM_CARD_ROTATIONS[i] + random.uniform(-5, 5), (3, 3))
            card = Card(self, *start_pos, "px", "tl", "ctr", card_data=card_data)

            card.move_anim(2 + i / 8, (6.5 * (i - 2), 0), "%", "ctr", "ctr",
                           call_on_finish=card.reveal)

            self.community_cards.add(card)

        anim_delay = 2 + len(self.community_cards) / 8
        ranking_int = self.game.the_player.player_hand.hand_ranking.ranking_type
        ranking_str = rules.basic.HandRanking.TYPE_STR[ranking_int].capitalize()
        if self.game.the_player.player_hand.folded:
            ranking_str = "Folded:  " + ranking_str

        app_timer.Timer(anim_delay, self.ranking_text.set_text_anim, (ranking_str,))
        app_timer.Timer(anim_delay + 0.25, self.highlight_cards)

        if len(self.game.deal.community_cards) == 3:
            app_timer.Timer(2, self.ranking_text.set_visible, (True,))
            self.hide_blinds_button()

        if skip_round:
            app_timer.Timer(anim_delay, self.game.deal.next_round)  # Skip round
        else:
            app_timer.Timer(anim_delay + 0.25, self.game.deal.start_new_round)  # Start new round

    def showdown(self):
        """
        Perform a showdown and reveal the winner(s) of the current deal.
        """

        self.ranking_text.set_visible(False)
        self.highlight_cards(unhighlight=True)
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
            app_timer.Timer(0.25, self.highlight_cards, (True,))

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
            winner_crown = WinnerCrown(self, player_display)
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
        self.hide_blinds_button()
        self.highlight_cards(unhighlight=True)

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
                card.move_anim(random.uniform(1.5, 2), card_end_pos)

            player.set_sub_text_anim("")  # Reset sub text

        # Community cards
        for card, rot in zip(self.community_cards.sprites(), COMM_CARD_ROTATIONS):
            card_end_pos = self.table.get_edge_coords(rot + random.uniform(-5, 5), (3, 3))
            card.move_anim(random.uniform(2, 2.5), card_end_pos)

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

    def move_dealer_button(self):
        """
        Move the dealer button to the player display of the current dealer. If there is currently no dealer button on
        the screen, then a new dealer button is made and moved from outside the screen.
        """

        if not self.dealer_button:
            start_pos = self.table.get_edge_coords(player_rotation(self.game.dealer, len(self.game.players)), (3, 3))
            self.dealer_button = DealerButton(self, *start_pos)
            self.all_sprites.add(self.dealer_button)

        dealer: PlayerDisplay = self.players.sprites()[self.game.dealer]
        new_pos = dealer.head_base.rect.global_rect.midright

        self.dealer_button.move_anim(1, new_pos, call_on_finish=self.new_blinds_button)

    def hide_dealer_button(self):
        """
        Hide the dealer button when the player displays get rearranged.
        """

        if not self.dealer_button:
            return

        def delete():
            self.all_sprites.remove(self.dealer_button)
            self.dealer_button = None

        animation = FadeAlpha(0.5, self.dealer_button, 255, 0, call_on_finish=delete)
        self.anim_group.add(animation)

    def new_blinds_button(self):
        """
        Create two blinds button (SB and BB) and move it to the respective player displays.
        """

        start_pos = self.dealer_button.rect.center

        # Initialize new buttons
        self.sb_button = DealerButton(self, *start_pos, "SB")
        self.bb_button = DealerButton(self, *start_pos, "BB")
        self.all_sprites.add(self.sb_button)
        self.all_sprites.add(self.bb_button)

        # Move SB button
        sb_player: PlayerDisplay = self.players.sprites()[self.game.deal.blinds[0]]
        sb_pos = sb_player.head_base.rect.global_rect.midright

        self.sb_button.move_anim(0.75, sb_pos)

        # Move BB button
        bb_player: PlayerDisplay = self.players.sprites()[self.game.deal.blinds[1]]
        bb_pos = bb_player.head_base.rect.global_rect.midright

        self.bb_button.move_anim(0.75, bb_pos)

    def hide_blinds_button(self):
        """
        Hide the blinds buttons (SB and BB) by adding alpha fade animations.
        """
        if not self.sb_button or not self.bb_button:
            return

        def delete():
            self.all_sprites.remove(self.sb_button)
            self.all_sprites.remove(self.bb_button)
            self.sb_button = None
            self.bb_button = None

        sb_animation = FadeAlpha(0.25, self.sb_button, 255, 0)
        bb_animation = FadeAlpha(0.25, self.bb_button, 255, 0, call_on_finish=delete)
        self.anim_group.add(sb_animation)
        self.anim_group.add(bb_animation)

    def update(self, dt):
        super().update(dt)

        if self.flash_fac > 0:
            self.display_surface.fill(3 * (self.flash_fac,), special_flags=pygame.BLEND_RGB_ADD)
