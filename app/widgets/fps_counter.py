import pygame

from app.shared import FontSave


class FPSCounter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = FontSave.get_font(2).render("-", True, "white")
        self.rect = self.image.get_rect(topleft=(5, 5))

        self.fps = 0

        self.last_update = 0
        self.frames = 0
        self.avg_dt = 0
        self.max_dt = 0

    def draw(self):
        self.image = FontSave.get_font(2).render(f"{self.fps:.0f} FPS;      "
                                                 f"Avg dt = {self.avg_dt * 1000:.1f} ms;     "
                                                 f"Max dt = {self.max_dt * 1000:.0f} ms", True, "white")
        self.rect = self.image.get_rect(topleft=(5, 5))

    def update(self, dt):
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
