import pygame

from app.animations import animation
from app.animations.animation import AnimGroup
from app.animations.fade import FadeSceneTransition
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
        self.display_surface = pygame.display.get_surface()

        self.clock = pygame.time.Clock()
        self.running = True

        """
        Scene and scene changing system
        """
        self.scene = MainMenuScene(self)
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
            Main updates
            """
            app_timer.default_group.update(dt)
            animation.default_group.update(dt)
            self.scene.update(dt)
            self.scene_transition_group.update(dt)

            pygame.display.update()

        pygame.quit()

    def change_scene(self, scene: Scene or str, cache_old_scene=True, duration=0.4):
        if duration > 0:
            if not self.scene_transition_group.animations:
                anim = FadeSceneTransition(duration, self, scene, cache_old_scene)
                self.scene_transition_group.add(anim)
            return

        elif self.scene_transition_group.animations:
            anim = self.scene_transition_group.animations[0]
            anim.pause()

        else:
            anim = None

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

                    case "game":
                        raise ValueError("cannot change to game scene by string id")

                    case _:
                        raise ValueError(f"invalid scene id: {scene}")

        else:
            raise TypeError("the scene argument must be a string or an instance of Scene")

        if cache_old_scene:
            self.scene_cache[old_scene.scene_id] = old_scene
        else:
            del old_scene

        if anim:
            anim.start()

    def quit(self):
        self.running = False
