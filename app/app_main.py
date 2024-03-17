import sys

import pygame

from app.scenes.game_scene import GameScene
from app.scenes.scene import Scene
from app.scenes.menu.main_menu import MainMenuScene
from app import app_timer
from app.widgets.listeners import KeyboardListener, MouseListener

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

        # self.scene = GameScene(self)
        self.scene = MainMenuScene(self)
        self.scene_stack = []  # Probably unused idk

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
                    KeyboardListener.broadcast(event)

                if event.type == pygame.MOUSEMOTION:
                    MouseListener.mouse_x, MouseListener.mouse_y = event.pos

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
                    MouseListener.broadcast(event)

            app_timer.update_timers(dt)
            self.scene.update(dt)
            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene, stack=False):
        if stack:
            self.scene_stack.append(self.scene)

        self.scene = scene

    def back_to_prev_scene(self):
        self.scene = self.scene_stack.pop(-1)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()
