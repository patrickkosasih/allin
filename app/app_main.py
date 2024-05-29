from typing import Callable

import pygame

from app.animations.animation import AnimGroup
from app.animations.fade import FadeSceneAnimation
from app.scenes.settings_scene import SettingsScene
from app.scenes.singleplayer_menu import SingleplayerMenuScene
from app.scenes.scene import Scene
from app.scenes.main_menu import MainMenuScene
from app.tools import app_timer
from app.widgets.listeners import MouseListener

WINDOWED_DIMENSIONS = 1280, 720
FPS = 60


class App:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Allin")
        pygame.display.set_icon(pygame.image.load("assets/sprites/misc/icon.png"))

        # pygame.key.set_repeat(500, 50)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)

        """
        Main systems
        """
        # self.screen = pygame.display.set_mode(WINDOWED_DIMENSIONS)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.display_surface = pygame.display.get_surface()

        self.clock = pygame.time.Clock()
        self.running = True

        """
        Scene and scene changing system
        """
        self.scene = MainMenuScene(self, startup_sequence=True)
        self.scene_cache = {}
        self.scene_transition_group = AnimGroup()

        self.reset_next_dt = False

    def run(self):
        while self.running:
            """
            Tick
            """
            dt = self.clock.tick(FPS) / 1000

            if self.reset_next_dt:
                dt = 1 / FPS
                self.reset_next_dt = False

            """
            Event loop
            """
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

            """
            Updates
            """
            app_timer.default_group.update(dt)
            self.scene.update(dt)
            self.scene_transition_group.update(dt)

            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene or str, cache_old_scene=True):
        old_scene = self.scene
        self.reset_next_dt = True

        if issubclass(type(scene), Scene):
            self.scene = scene

        elif type(scene) is str:
            if scene in self.scene_cache and scene != "":
                self.scene = self.scene_cache[scene]

            else:
                match scene:
                    case "mainmenu":
                        self.scene = MainMenuScene(self)

                    case "singleplayer":
                        self.scene = SingleplayerMenuScene(self)

                    case "settings":
                        self.scene = SettingsScene(self)

                    case "game":
                        raise ValueError("cannot change to game scene by string id")

                    case _:
                        raise ValueError(f"invalid scene id: {scene}")

        elif callable(scene):
            self.scene = scene()

        else:
            raise TypeError("the scene argument must be either a string, an instance of Scene, or a function that"
                            "returns a Scene instance")

        if cache_old_scene:
            self.scene_cache[old_scene.scene_id] = old_scene
        else:
            del old_scene

    def change_scene_anim(self, scene: Scene or str or Callable[[None], Scene], cache_old_scene=True, duration=0.2):
        if self.scene_transition_group.animations:
            return

        app_timer.Sequence([
            lambda: FadeSceneAnimation(duration, self, 0, 255, anim_group=self.scene_transition_group),
            duration,
            lambda: self.change_scene(scene, cache_old_scene),
            lambda: FadeSceneAnimation(duration, self, 255, 0, anim_group=self.scene_transition_group)
        ])

    def quit(self):
        self.running = False
