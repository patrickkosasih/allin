import rules.game_flow
from app.scenes.scene import Scene
from app.shared import *
from app import widgets


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.game = rules.game_flow.PokerGame(6)

        self.table = widgets.table.Table(percent_to_px(50, 50), percent_to_px(65, 65))
        self.all_sprites.add(self.table)

        # Card test
        self.cards = []
        deck_iter = iter(self.game.deal.deck)
        for i in range(-2, 3):
            card = widgets.card.Card(percent_to_px(50 + 6.5 * i, 50), h_percent_to_px(12.5), next(deck_iter))
            self.cards.append(card)
            self.all_sprites.add(card)

        self.thing = widgets.button.Button(percent_to_px(50, 50), percent_to_px(15, 7.5), text="Hi",
                                           command=lambda: print("Hello, World!"), b_thickness=5)
        self.all_sprites.add(self.thing)

    def update(self):
        super().update()
