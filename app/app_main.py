import sys
from typing import Callable

import pygame

from app.scenes.game_scene import GameScene
from app.scenes.menu.singleplayer_menu import SingleplayerMenuScene
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
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)

        # self.screen = pygame.display.set_mode(WINDOWED_DIMENSIONS)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True

        # self.scene = GameScene(self)
        self.scene = MainMenuScene(self)

    def run(self):
        while self.running:
            """
            The main loop
            """

            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    self.scene.broadcast_keyboard(event)

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        MouseListener.mouse_down = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        MouseListener.mouse_down = False

                    self.scene.broadcast_mouse(event)

                if event.type == pygame.MOUSEMOTION:
                    MouseListener.mouse_x, MouseListener.mouse_y = event.pos

            app_timer.update_timers(dt)
            self.scene.update(dt)
            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene or str, **kwargs):
        if issubclass(type(scene), Scene):
            self.scene = scene

        elif type(scene) is str:
            match scene:
                case "mainmenu":
                    self.scene = MainMenuScene(self)

                case "singleplayer":
                    self.scene = SingleplayerMenuScene(self)

                case "game":
                    self.scene = GameScene(self, **kwargs)

                case _:
                    raise ValueError(f"invalid scene key string: {scene}")

        else:
            raise TypeError("the scene argument must be a string or an instance of Scene")

    def quit(self):
        self.running = False
