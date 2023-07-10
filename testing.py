"""
testing.py

A module for early testing and basic interface to the poker game before the GUI is implemented.
"""

import rules


def standard_io_poker():
    game = rules.PokerGame(4)

    print([rules.card_str(card) for card in game.hand.deck])

    for i, player in enumerate(game.hand.player_hands):
        print(f"Player {i + 1}: {[rules.card_str(card) for card in player.pocket_cards]} ; ${player.player_data.money:,}")
