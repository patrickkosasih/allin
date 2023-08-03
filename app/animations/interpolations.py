"""
app/animations/interpolations.py


"""


def linear(x):
    return x


def ease_in_out(x: float, power: float = 2.0) -> float:
    if x <= 0.5:
        return (2 * x) ** power / 2
    else:
        return 1 - (2 - 2 * x) ** power


def back_and_forth(x: float, power: float = 1.0) -> float:
    return (-4 * x * (x - 1)) ** power
