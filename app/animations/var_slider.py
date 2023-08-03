from typing import Callable

from app.animations.animation import Animation
from app.animations.interpolations import *


NONE_FUNC = lambda x=None: None
DEFAULT_INTERPOLATION = lambda x: ease_in_out(x, power=3)


class VarSlider(Animation):
    """
    The variable slider is a simple yet flexible class which can be used for a variety of animations.

    A variable slider has a changing value `current_val` that is updated every tick, and a setter function `setter_func`
    that is called with the current value as an argument. While the animation is running, the changing value slides from
    the start value to the end value.
    """

    def __init__(self, duration, start_val: float, end_val: float,
                 interpolation: Callable[[float], float] = DEFAULT_INTERPOLATION,
                 setter_func: Callable[[float], None] = NONE_FUNC,
                 finish_func: Callable = NONE_FUNC):
        """
        :param duration: The duration of the animation.
        :param start_val: The starting value.
        :param end_val: The value to slide to.
        :param interpolation: The interpolation function that converts the phase into the interpolated phase.
        :param setter_func: The function that is called after every update with the current value passed in as an
        argument.
        :param finish_func: The function that is called after the animation has finished.
        """

        super().__init__(duration)

        self.start_val = start_val
        self.end_val = end_val
        self.current_val = start_val

        self.interpolation = interpolation
        self.setter_func = setter_func
        self.finish_func = finish_func

    def update_anim(self):
        interpol_phase = self.interpolation(self.phase)
        self.current_val = self.start_val + (self.end_val - self.start_val) * interpol_phase
        self.setter_func(self.current_val)

    def finish(self):
        self.update_anim()
        self.finish_func()
