import pygame

from app import global_settings
from app.scenes.scene import Scene
from app.shared import load_image
from app.widgets.basic.button import CircularButton
from app.widgets.basic.game_bg import GameBackground
from app.widgets.menu.setting_panel import SettingPanel, SettingEntry


class SettingsScene(Scene):
    def __init__(self, app):
        super().__init__(app, "settings")

        self.background = GameBackground(self, 0, 0, 101, 100, "%w", "ctr", "ctr")
        self.background.image.set_alpha(200)

        self.setting_panel = SettingPanel(self, 0, 0, 75, 75, "%", "ctr", "ctr",
                                          settings_data=global_settings.app_settings,
                                          main_header_str="Settings",
                                          base_color=(24, 31, 37, 200),
                                          base_radius=5, pack_height=12, entry_horizontal_margin=3)

        self.setting_panel.entries["fps_limit"].call_on_change = lambda x: print(x)

        """
        Buttons
        """
        self.back_button = CircularButton(self, 1.5, 1.5, 4, "%h", "tl", "tl",
                                          command=self.back,
                                          icon=load_image("assets/sprites/menu icons/back.png"),
                                          icon_size=0.8)

    def back(self):
        self.app.change_scene_anim("mainmenu")
        self.setting_panel.settings_data.save()
