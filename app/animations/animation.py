from abc import ABC, abstractmethod


class Animation(ABC):
    def __init__(self, duration):
        self.duration = duration
        self.phase = 0
        self.finished = False

    def update(self, dt):
        self.phase += dt / self.duration

        if self.phase >= 1:
            self.finish()
            self.phase = 1
            self.finished = True
        else:
            self.update_anim()

    @abstractmethod
    def update_anim(self):
        pass

    @abstractmethod
    def finish(self):
        pass
