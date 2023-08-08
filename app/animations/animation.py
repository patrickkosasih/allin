from abc import ABC, abstractmethod
from typing import Callable

from app.animations.interpolations import InterpolationFunc, ease_in_out


class Animation(ABC):
    """
    `Animation` is the base class for all animation classes.
    """

    def __init__(self, duration: float,
                 interpolation: InterpolationFunc = ease_in_out,
                 call_on_finish: Callable = lambda: None):
        """
        Initialize the animation (superclass).

        :param duration: The duration of the animation.
        :param interpolation: The interpolation function that converts `phase` into `interpol_phase`.
        :param call_on_finish: An external function that is called when the function is finished (optional).
        """
        self.duration = duration
        self.phase = 0
        self.finished = False

        self.interpolation = interpolation
        self.interpol_phase = 0

        self.call_on_finish = call_on_finish

    def update(self, dt):
        if self.finished:
            return

        self.phase += dt / self.duration
        self.interpol_phase = self.interpolation(self.phase)

        if self.phase >= 1:
            self.finish()
            self.call_on_finish()
            self.phase = 1
            self.finished = True
        else:
            self.update_anim()

    @abstractmethod
    def update_anim(self) -> None:
        """
        Abstract method: Called on every update.
        """
        pass

    @abstractmethod
    def finish(self) -> None:
        """
        Abstract method: Called once the animation is finished playing.
        """
        pass
