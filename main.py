"""
main.py

Welcome to the Allin source code! Programmed by Patrick Kosasih.
This is the gateway of running the entire Allin app.
"""

# import testing
# from rules.basic import HandRanking
from app.app_main import App


def main():
    App().run()
    # testing.standard_io_poker()
    # testing.hand_ranking_test(repeat_until=rules.HandRanking.ROYAL_FLUSH)
    # testing.hand_ranking_test(n_tests=25)


if __name__ == "__main__":
    main()
