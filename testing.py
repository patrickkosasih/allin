"""
testing.py

A module for early testing and basic interface to the poker game before the GUI is implemented.
"""
import random
import time

from rules.basic import *
from rules.game_flow import *


class LegacyTestingGame(PokerGame):
    def __init__(self, n_players: int):
        super().__init__()

        if n_players >= 2:
            self.auto_start_game(n_players)

    def auto_start_game(self, n_players):
        self.players = [Player(self, f"Player {i + 1}", 1000) for i in range(n_players)]
        self.new_deal()
        self.deal.start_deal()


"""
==============
String formats
==============
"""
PLAYER_STATE_FORMAT = "{turn_arrow: <3}{name: <15}{pocket_cards: <10}${money: <10}{ranking: <18} {action: <15}"


"""
=======================
Output helper functions
=======================
"""
def print_state(game: PokerGame):
    """
    Prints the state of the current game/hand:

    1. Player states:
        a. An arrow (->) for the current turn player
        b. Player name
        c. Pocket cards
        d. Money
        e. Dealer, small blinds, big blinds (on preflop round); or
           Current hand ranking (after the flop)
        f. Player action

    2. Pot
    3. Community cards
    """

    for player in game.deal.players:  # player: PlayerHand
        is_preflop = bool(not game.deal.community_cards)
        preflop_role = ""
        ranking = HandRanking.TYPE_STR[player.hand_ranking.ranking_type].capitalize() if not is_preflop else "n/a"

        if is_preflop:
            # If the current round is still the preflop round then determine the D, SB, and BB
            players = game.deal.players

            if player is players[game.dealer]:
                preflop_role = "D"
            elif player is players[game.deal.blinds[0]]:
                preflop_role = "SB"
            elif player is players[game.deal.blinds[1]]:
                preflop_role = "BB"

        print(PLAYER_STATE_FORMAT.format(
            turn_arrow="-> " if player is game.deal.get_current_player() else "",
            name=player.player_data.name,
            pocket_cards=card_list_str(player.pocket_cards),
            money=f"{player.player_data.money:,}",
            ranking=ranking if not is_preflop else preflop_role,
            action=f"{player.last_action.capitalize()} {f'${player.bet_amount:,}' if player.bet_amount > 0 else ''}",
        ))

    print(f"\nPot: ${game.deal.current_round_pot:,} -> Main pot: ${game.deal.pots[0]:,}"
          f", Side pots: {' '.join(f'${x:,}' for x in game.deal.pots[1:])}\n"
          f"Community cards: {card_list_str(game.deal.community_cards)}")


def print_winner(game: PokerGame):
    """
    Print the winner(s) of the deal when a deal ends by showdown or everyone folding.
    """
    for player in game.deal.players:
        ranking = HandRanking.TYPE_STR[player.hand_ranking.ranking_type].capitalize()

        win = player in game.deal.winners
        new_money = player.player_data.money
        old_money = new_money - game.deal.pot // len(game.deal.winners)

        winner_text = f"WINNER!  ${old_money:,} -> ${new_money:,}" if win else ("Folded" if player.folded else "")

        print(PLAYER_STATE_FORMAT.format(
            turn_arrow="-> " if win else "",
            name=player.player_data.name,
            pocket_cards=card_list_str(player.pocket_cards),
            money=f"{old_money if win else new_money}",
            ranking=ranking,
            action=winner_text,
        ))

    if len(game.deal.winners) > 1:
        split_pot_text = f" --> Split: ${game.deal.pot:,} / {len(game.deal.winners)} = " \
                         f"{game.deal.pot // len(game.deal.winners):,}"
    else:
        split_pot_text = ""

    print(f"\nPot: ${game.deal.pot:,}{split_pot_text}\n"
          f"Community cards: {card_list_str(game.deal.community_cards)}")


def card_list_str(cards: list[Card]) -> str:
    """
    Returns a readable string format for a list of cards.
    e.g. "J♠ 10♣ 7♣ 6♥ A♦"
    """
    return " ".join([card_str(card) for card in cards])


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

    game = LegacyTestingGame(6)

    while True:
        print("\n" + "=" * 80 + "\n")

        if game.deal.winners:
            print_winner(game)
            print()
            game.new_deal()

            if len(game.players) < 2:
                print(f"{game.players[0].name} is the last one standing with ${game.players[0].money:,}!")
                break
            else:
                input("Press enter to start next deal. ")
                continue

        print_state(game)
        print()

        player_name = game.deal.get_current_player().player_data.name  # Name of the current turn player
        action = input(f"What will {player_name} do? ").upper().split()
        # The input is uppercased and then split into a list.

        new_amount = 0  # New amount for betting/raising
        # action = ["CALL"]

        try:
            if action[0] == "QUIT":
                break

            if action[0] in ("BET", "RAISE"):
                if len(action) < 2:
                    print("Specify a betting amount.")
                    continue

                new_amount = int(action[1])

            action_code = Actions.__dict__[action[0]]
            game.deal.action(action_code, new_amount)

            if game.deal.round_finished:
                game.deal.next_round()
                game.deal.start_new_round()

        except (IndexError, KeyError):
            print("Invalid input.")

        except ValueError as e:
            print("Invalid betting amount:", e)


def hand_ranking_test(n_tests=10, repeat_until=0):
    deck = generate_deck()
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
        ranking = HandRanking(cards)
        t = time.perf_counter() - t

        print(table_format.format(pocket=card_list_str(cards[:2]),
                                  community=card_list_str(cards[2:]),
                                  ranking_type=HandRanking.TYPE_STR[ranking.ranking_type].capitalize(),
                                  ranked_cards=card_list_str(ranking.ranked_cards),
                                  kickers=card_list_str(ranking.kickers),
                                  tiebreaker_score=ranking.tiebreaker_score,
                                  exec_time=f"{t * 1E6: .5} μs"))

        if ranking.ranking_type == repeat_until or (i >= n_tests and repeat_until == 0):
            break

    print("Repeats:", i)


if __name__ == "__main__":
    standard_io_poker()
    # hand_ranking_test(repeat_until=HandRanking.ROYAL_FLUSH)
    # hand_ranking_test(n_tests=25)
