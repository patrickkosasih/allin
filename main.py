import testing
import rules


def main():
    # testing.standard_io_poker()
    testing.hand_ranking_test(repeat_until=rules.HandRanking.ROYAL_FLUSH)
    # testing.hand_ranking_test(n_tests=25)


if __name__ == "__main__":
    main()
