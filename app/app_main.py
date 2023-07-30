import pygame

from app.scenes.game_scene import GameScene
from app.shared import FontSave


WINDOWED_DIMENSIONS = 1280, 720
FPS = 60


class App:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Allin")

        # self.screen = pygame.display.set_mode(WINDOWED_DIMENSIONS)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = GameScene()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene.update()
            self.draw_fps(dt)
            pygame.display.update()

        pygame.quit()

    def draw_fps(self, dt):
        fps_text = FontSave.get_font(2).render(f"{1 / dt:.0f} FPS      {dt * 1000:.0f} ms update", True, "white")
        self.screen.blit(fps_text, fps_text.get_rect(topleft=(5, 5)))
