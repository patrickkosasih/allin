"""
testing.py

A module for early testing and basic interface to the poker game before the GUI is implemented.
"""

import rules


def print_state(game: rules.PokerGame):
    """
    Prints the state of the current game/hand:

    1. Player states:
        a. An arrow (->) for the current turn player
        b. Player name
        c. Pocket cards
        d. Money
        e. Called/folded?
        f. Dealer, small blinds, big blinds (only on preflop round)

    2. Pot
    3. Community cards

    """

    for player in game.current_hand.players:
        print(f"{'-> ' if player is game.current_hand.get_current_player() else '   '}"
              f"{player.player_data.name}: {[rules.card_str(card) for card in player.pocket_cards]}; "
              f"${player.player_data.money:,}; "
              f"{'Folded' if player.folded else ('Called' if player.called else '')} ", end="")

        if not game.current_hand.community_cards:
            # If the current round is still the preflop round then determine the D, SB, and BB
            players = game.current_hand.players

            if player is players[game.dealer]:
                print("D")
            elif player is players[game.current_hand.blinds[0]]:
                print("SB")
            elif player is players[game.current_hand.blinds[1]]:
                print("BB")
            else:
                print()

        else:
            print()


    print(f"\nPot: {game.current_hand.pot}\n"
          f"Community cards: {[rules.card_str(card) for card in game.current_hand.community_cards]}")


def standard_io_poker():
    """
    Run a text based poker game using the console's basic input and output.

    To play, type in the actions of each player (not case-sensitive). Actions can be the following:
    1. Fold
    2. Check
    3. Call
    4. Bet <bet amount>
    5. Raise <new bet amount>

    Note that check and call does the same thing; and bet and raise also does the same thing.
    """

    game = rules.PokerGame(6)

    # print([rules.card_str(card) for card in game.current_hand.deck])

    while True:
        print("\n" + "=" * 50 + "\n")
        print_state(game)
        print()

        player_name = game.current_hand.get_current_player().player_data.name  # Name of the current turn player
        action = input(f"What will {player_name} do? ").upper().split()
        # The input is uppercased and then split into a list.
        new_amount = 0
        # New amount for betting/raising

        try:
            if action[0] == "QUIT":
                break

            if action[0] in ("BET", "RAISE"):
                if len(action) < 2:
                    print("Specify a betting amount.")
                    continue

                new_amount = int(action[1])

            action_code = rules.Actions.__dict__[action[0]]
            game.current_hand.action(action_code, new_amount)

        except (IndexError, KeyError):
            print("Invalid input.")

        except ValueError as e:
            print("Invalid betting amount:", e)
