import pygame.image

from app.animations.interpolations import ease_out
from app.scenes.scene import Scene
from app.tools import app_timer
from app.tools.app_timer import Coroutine
from app.widgets.basic.game_bg import GameBackground
from app.widgets.basic.button import Button
from app.shared import *
from app.widgets.menu.welcome_text import WelcomeText

MAIN_MENU_BUTTON_COLOR = (24, 31, 37, 169)


class MainMenuScene(Scene):
    def __init__(self, app, startup_sequence=False):
        super().__init__(app, "mainmenu")
        self.bg_color = "#000000"

        self.background = GameBackground(self, 0, 0, 101, 101, "%w", "ctr", "ctr")
        self.welcome_text = None

        self.singleplayer_button = Button(self, -11, -7.5, 20, 50, "%", "ctr", "ctr", text_str="Singleplayer",
                                          rrr=h_percent_to_px(5), b_thickness=0, color=MAIN_MENU_BUTTON_COLOR,
                                          font=FontSave.get_font(5),
                                          icon=load_image("assets/sprites/menu icons/singleplayer.png"),
                                          icon_size=0.6, text_align="bottom", icon_align="middle", text_align_offset=0.04,
                                          command=self.singleplayer_click)

        self.multiplayer_button = Button(self, 11, -7.5, 20, 50, "%", "ctr", "ctr", text_str="Multiplayer",
                                         rrr=h_percent_to_px(5), b_thickness=0, color=MAIN_MENU_BUTTON_COLOR,
                                         font=FontSave.get_font(5),
                                         icon=load_image("assets/sprites/menu icons/multiplayer.png"),
                                         icon_size=0.6, text_align="bottom", icon_align="middle", text_align_offset=0.04,
                                         command=lambda: print("Multiplayer come'th soon..."))

        self.settings_button = Button(self, -11, 25, 20, 10, "%", "ctr", "ctr", text_str="Settings",
                                      b_thickness=0, color=MAIN_MENU_BUTTON_COLOR, font=FontSave.get_font(5),
                                      icon=load_image("assets/sprites/menu icons/settings.png"), icon_size=0.8,
                                      command=self.settings_click)

        self.quit_button = Button(self, 11, 25, 20, 10, "%", "ctr", "ctr", text_str="Quit",
                                  b_thickness=0, color=MAIN_MENU_BUTTON_COLOR, font=FontSave.get_font(5),
                                  icon=load_image("assets/sprites/menu icons/quit.png"), icon_size=0.8,
                                  command=self.app.quit)

        self.buttons = [self.singleplayer_button, self.multiplayer_button, self.settings_button, self.quit_button]

        if startup_sequence:
            self.startup_sequence()

    """
    Start-up sequence
    """

    def startup_sequence(self):
        for _ in self.set_buttons_shown(False, 0, 0):
            pass

        self.background.set_pos(0, -100, "%", "mb", "mb")
        self.background.image.set_alpha(0)

        self.welcome_text = WelcomeText(self, 0, 0, 50, 50, "%", "ctr", "ctr")

        app_timer.Sequence([
            1.5,
            lambda: self.background.move_anim(3, (0, 0), "px", "ctr", "ctr",
                                              interpolation=lambda x: ease_out(x, power=2.5)),
            lambda: self.background.fade_anim(4, 255),

            2, lambda: self.welcome_text.fade_anim(1.5, 0),
            1, lambda: Coroutine(self.set_buttons_shown(True, 0.5, 0.15)),
            1.5, lambda: self.welcome_text.delete("welcome_text")
        ])

    def set_buttons_shown(self, shown: bool, duration: float, interval: float):
        for button in self.buttons:
            button.fade_anim(duration, 255 if shown else 0)
            button.disabled = not shown

            if interval > 0:
                yield interval

    """
    Button commands
    """

    def singleplayer_click(self):
        self.app.change_scene_anim("singleplayer")

    def settings_click(self):
        self.app.change_scene_anim("settings")
