"""
app/animations/interpolations.py

The module that contains interpolation functions: functions that convert the animation phase into the interpolated
phase, making animations much more pleasing to look at.
"""

from typing import Callable


InterpolationFunc = Callable[[float], float]
"""An interpolation function is defined as a function that converts the animation phase into the interpolated
phase (float argument -> float return value). The animation phase and interpolated phase must both be between 0 and 1."""


def linear(x):
    return x


def ease_in_out(x: float, power: float = 2.0) -> float:
    if x <= 0.5:
        return (2 * x) ** power / 2
    else:
        return 1 - (2 - 2 * x) ** power / 2


def ease_in(x: float, power: float = 2.0) -> float:
    return x ** power


def ease_out(x: float, power: float = 2.0) -> float:
    return (-x * (x - 2)) ** (1 / power)
