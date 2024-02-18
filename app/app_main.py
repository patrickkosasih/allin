import sys

import pygame

import app.shared
from app.scenes.scene import Scene
from app.scenes.game_scene import GameScene
from app.scenes.main_menu import MainMenuScene
from app import app_timer


WINDOWED_DIMENSIONS = 1280, 720
FPS = 60


class App:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Allin")
        pygame.display.set_icon(pygame.image.load("assets/sprites/misc/icon.png"))
        pygame.key.set_repeat(500, 50)

        # self.screen = pygame.display.set_mode(WINDOWED_DIMENSIONS)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = MainMenuScene(self)
        # self.scene = GameScene(self)

    def run(self):
        while self.running:
            """
            The main loop
            """

            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    app.shared.KeyBroadcaster.broadcast(event)

            app_timer.update_timers(dt)
            self.scene.update(dt)
            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene):
        self.scene = scene

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()
