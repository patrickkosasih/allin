"""
testing.py

A module for early testing and basic interface to the poker game before the GUI is implemented.
"""
import random
import time

import rules


"""
=======================
Output helper functions
=======================
"""
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

    for player in game.current_deal.players:
        print(f"{'-> ' if player is game.current_deal.get_current_player() else '   '}"
              f"{player.player_data.name}: {[rules.card_str(card) for card in player.pocket_cards]}; "
              f"${player.player_data.money:,}; "
              f"{'Folded' if player.folded else ('Called' if player.called else '')} ", end="")

        if not game.current_deal.community_cards:
            # If the current round is still the preflop round then determine the D, SB, and BB
            players = game.current_deal.players

            if player is players[game.dealer]:
                print("D")
            elif player is players[game.current_deal.blinds[0]]:
                print("SB")
            elif player is players[game.current_deal.blinds[1]]:
                print("BB")
            else:
                print()

        else:
            print()


    print(f"\nPot: {game.current_deal.pot}\n"
          f"Community cards: {[rules.card_str(card) for card in game.current_deal.community_cards]}")


def card_list_str(cards: list[rules.Card]) -> str:
    """
    Returns a readable string format for a list of cards.
    e.g. "J♠ 10♣ 7♣ 6♥ A♦"
    """
    return " ".join([rules.card_str(card) for card in cards])


"""
=====================
Run on main functions
=====================
"""
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

        player_name = game.current_deal.get_current_player().player_data.name  # Name of the current turn player
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
            game.current_deal.action(action_code, new_amount)

        except (IndexError, KeyError):
            print("Invalid input.")

        except ValueError as e:
            print("Invalid betting amount:", e)


def hand_ranking_test(n_tests=10, repeat_until=0):
    deck = rules.generate_deck()
    table_format = "{pocket: <20}{community: <20}{ranking_type: <20}{ranked_cards: <20}{kickers: <20}" \
                   "{tiebreaker_score: <20}{exec_time}"

    print(table_format.format(pocket="Pocket cards",
                              community="Community cards",
                              ranking_type="Ranking type",
                              ranked_cards = "Ranked cards",
                              kickers="Kickers",
                              tiebreaker_score="Tiebreaker score",
                              exec_time="Execution time"))

    # for i in range(tests):
    i = 0
    while True:
        i += 1

        cards = [deck[x] for x in random.sample(range(52), 7)]
        t = time.perf_counter()
        ranking = rules.HandRanking(cards)
        t = time.perf_counter() - t

        print(table_format.format(pocket=card_list_str(cards[:2]),
                                  community=card_list_str(cards[2:]),
                                  ranking_type=rules.HandRanking.TYPE_STR[ranking.ranking_type].capitalize(),
                                  ranked_cards=card_list_str(ranking.ranked_cards),
                                  kickers=card_list_str(ranking.kickers),
                                  tiebreaker_score=ranking.tiebreaker_score,
                                  exec_time=f"{t * 1E6: .5} μs"))

        if ranking.ranking_type == repeat_until or (i >= n_tests and repeat_until == 0):
            break

    print("Repeats:", i)
