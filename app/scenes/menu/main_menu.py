import pygame.image

from app.scenes.game_scene import GameScene
from app.scenes.menu.singleplayer_menu import SingleplayerMenuScene
from app.scenes.scene import Scene
from app.widgets.basic.button import Button
from app.shared import *


MAIN_MENU_BUTTON_COLOR = (24, 31, 37, 128)


class MainMenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)

        self.singleplayer_button = Button(self, -11, -7.5, 20, 50, "%", "ctr", "ctr", text_str="Singleplayer",
                                          rrr=h_percent_to_px(5), b_thickness=0, color=MAIN_MENU_BUTTON_COLOR,
                                          font=FontSave.get_font(5),
                                          icon=pygame.image.load("assets/sprites/menu icons/singleplayer.png"),
                                          icon_size=0.6, text_align="bottom", icon_align="middle", text_align_offset=0.04,
                                          command=self.singleplayer_click)

        self.multiplayer_button = Button(self, 11, -7.5, 20, 50, "%", "ctr", "ctr", text_str="Multiplayer",
                                         rrr=h_percent_to_px(5), b_thickness=0, color=MAIN_MENU_BUTTON_COLOR,
                                         font=FontSave.get_font(5),
                                         icon=pygame.image.load("assets/sprites/menu icons/multiplayer.png"),
                                         icon_size=0.6, text_align="bottom", icon_align="middle", text_align_offset=0.04)

        self.settings_button = Button(self, -11, 25, 20, 10, "%", "ctr", "ctr", text_str="Settings",
                                      b_thickness=0, color=MAIN_MENU_BUTTON_COLOR, font=FontSave.get_font(5),
                                      icon=pygame.image.load("assets/sprites/menu icons/settings.png"), icon_size=0.8)

        self.quit_button = Button(self, 11, 25, 20, 10, "%", "ctr", "ctr", text_str="Quit",
                                  b_thickness=0, color=MAIN_MENU_BUTTON_COLOR, font=FontSave.get_font(5),
                                  icon=pygame.image.load("assets/sprites/menu icons/quit.png"), icon_size=0.8,
                                  command=self.app.quit)

    def singleplayer_click(self):
        self.app.change_scene(SingleplayerMenuScene(self.app))
