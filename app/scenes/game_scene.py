import pygame.sprite

import rules.singleplayer

from app.scenes.scene import Scene
from app.shared import *
from app import widgets


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.game = rules.singleplayer.SingleplayerGame(6, self.on_any_action, self.on_turn)

        self.table = widgets.table.Table(percent_to_px(50, 50), percent_to_px(55, 55))
        self.all_sprites.add(self.table)

        self.players = pygame.sprite.Group()
        self.init_players()

        # Card test
        self.cards = pygame.sprite.Group()
        deck_iter = iter(self.game.deal.deck)

        for i in range(-2, 3):
            card = widgets.card.Card(percent_to_px(50 + 6.5 * i, 50), h_percent_to_px(12.5), next(deck_iter))
            self.cards.add(card)
            self.all_sprites.add(card)

        # self.thing = widgets.button.Button(percent_to_px(50, 50), percent_to_px(15, 7.5), text="Hi",
        #                                    command=lambda: print("Hello, World!"), b_thickness=5)
        # self.all_sprites.add(self.thing)

    def on_any_action(self):
        pass

    def on_turn(self):
        pass

    def init_players(self):
        player_angle = 360 / len(self.game.players)  # The angle between players in degrees

        for i, player_data in enumerate(self.game.players):
            player = widgets.player_display.PlayerDisplay(self.table.get_edge_coords(i * player_angle + 90, (1.25, 1.2)),
                                                          percent_to_px(15, 12.5),
                                                          player_data)
            self.players.add(player)
            self.all_sprites.add(player)

    def deal_cards(self):
        pass

    def update(self):
        super().update()
