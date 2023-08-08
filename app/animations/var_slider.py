from typing import Callable

from app.animations.animation import Animation
from app.animations.interpolations import *


NONE_FUNC = lambda x=None: None


class VarSlider(Animation):
    """
    The variable slider is a simple yet flexible class which can be used for a variety of animations.

    A variable slider has a changing value `current_val` that is updated every tick, and a setter function `setter_func`
    that is called with the current value as an argument. While the animation is running, the changing value slides from
    the start value to the end value.
    """

    def __init__(self, duration, start_val: float, end_val: float,
                 setter_func: Callable[[float], None] = NONE_FUNC,
                 **kwargs):
        """
        :param duration: The duration of the animation.
        :param start_val: The starting value.
        :param end_val: The value to slide to.
        :param interpolation: The interpolation function that converts the phase into the interpolated phase.
        :param setter_func: The function that is called after every update with the current value passed in as an
        argument.
        """

        super().__init__(duration, **kwargs)

        self.start_val = start_val
        self.end_val = end_val
        self.current_val = start_val

        self.setter_func = setter_func

    def update_anim(self):
        self.current_val = self.start_val + self.interpol_phase * (self.end_val - self.start_val)
        self.setter_func(self.current_val)

    def finish(self):
        self.update_anim()
