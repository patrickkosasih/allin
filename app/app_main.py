import pygame

from app.scenes.game_scene import GameScene
from app.scenes.menu.singleplayer_menu import SingleplayerMenuScene
from app.scenes.scene import Scene
from app.scenes.menu.main_menu import MainMenuScene
from app.tools import app_timer
from app.widgets.listeners import MouseListener

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

        """
        Main systems
        """
        # self.screen = pygame.display.set_mode(WINDOWED_DIMENSIONS)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True

        """
        Scene and scene changing system
        """
        self.scene = MainMenuScene(self)
        self.scene_cache = {}

        self.reset_next_dt = False

    def run(self):
        while self.running:
            """
            Tick
            """
            dt = self.clock.tick(FPS) / 1000

            if self.reset_next_dt:
                dt = 1 / FPS

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
            Main updates
            """
            app_timer.default_group.update(dt)
            self.scene.update(dt)
            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene or str, cache_old_scene=True, **kwargs):
        old_scene = self.scene

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

                    case "game":
                        self.scene = GameScene(self, **kwargs)

                    case _:
                        raise ValueError(f"invalid scene key string: {scene}")

        else:
            raise TypeError("the scene argument must be a string or an instance of Scene")

        if cache_old_scene:
            self.scene_cache[old_scene.scene_id] = old_scene
        else:
            del old_scene

    def quit(self):
        self.running = False
