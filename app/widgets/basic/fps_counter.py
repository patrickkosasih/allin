import pygame

from app.shared import FontSave
from app.widgets.listeners import KeyboardListener
from app.widgets.widget import Widget


class FPSCounter(KeyboardListener):
    """
    The FPS counter shows the FPS, average delta time, and max delta time on the last second.
    Press F3 to toggle the FPS counter.
    """

    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)

        self.fps = 0

        self.last_update = 0
        self.frames = 0
        self.avg_dt = 0
        self.max_dt = 0

        self.shown = False

    def draw(self):
        self.image = FontSave.get_font(2).render(f"{self.fps:.0f} FPS;      "
                                                 f"Avg dt = {self.avg_dt * 1000:.1f} ms;     "
                                                 f"Max dt = {self.max_dt * 1000:.0f} ms", True, "white")

    def key_down(self, event):
        if event.key == pygame.K_F3:
            self.shown = not self.shown

            if self.shown:
                self.image = FontSave.get_font(2).render("-", True, "white")
            else:
                self.image = pygame.Surface((1, 1), pygame.SRCALPHA)

    def update(self, dt):
        if not self.shown:
            return

        self.last_update += dt

        self.frames += 1
        self.max_dt = max(self.max_dt, dt)

        if self.last_update >= 1:
            self.last_update -= 1

            self.fps = self.frames
            self.avg_dt = 1 / self.frames

            self.draw()

            self.frames = 0
            self.max_dt = 0
