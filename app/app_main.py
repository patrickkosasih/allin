import pygame

from app.scenes.game_scene import GameScene


DEFAULT_WIDTH, DEFAULT_HEIGHT = 1280, 720
FPS = 60


class App:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Allin")

        # self.screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = GameScene()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene.update()
            pygame.display.update()

            self.clock.tick(FPS)

        pygame.quit()
