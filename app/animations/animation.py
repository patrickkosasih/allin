from abc import ABC, abstractmethod
from typing import Callable


class Animation(ABC):
    """
    `Animation` is the base class for all animation classes.
    """

    def __init__(self, duration: float, call_on_finish: Callable = lambda: None):
        """
        Initialize the animation (superclass).

        :param duration: The duration of the animation.
        :param call_on_finish: An external function that is called when the function is finished (optional).
        """
        self.duration = duration
        self.phase = 0
        self.finished = False

        self.call_on_finish = call_on_finish

    def update(self, dt):
        self.phase += dt / self.duration

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
