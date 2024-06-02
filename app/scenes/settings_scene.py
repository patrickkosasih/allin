import pygame

from app import app_settings, audio
from app.scenes.scene import Scene
from app.shared import load_image
from app.widgets.basic.button import CircularButton
from app.widgets.basic.game_bg import GameBackground
from app.widgets.menu.setting_panel import SettingPanel, SettingEntry


class SettingsScene(Scene):
    def __init__(self, app, scroll_offset=0):
        super().__init__(app, "settings")

        self.background = GameBackground(self, 0, 0, 101, 100, "%w", "ctr", "ctr")
        self.background.image.set_alpha(200)

        self.setting_panel = SettingPanel(self, 0, 0, 75, 75, "%", "ctr", "ctr",
                                          settings_data=app_settings.main,
                                          main_header_str="Settings",
                                          base_color=(24, 31, 37, 200),
                                          base_radius=5, pack_height=12, entry_horizontal_margin=3)

        self.setting_panel.scroll_offset = scroll_offset

        self.setting_panel.entries["sfx_volume"].call_on_change = audio.default_group.update_volume
        self.setting_panel.entries["background"].call_on_change = lambda: self.on_display_change(force_update=True)

        for x in ("windowed", "window_resolution", "fps_limit"):
            self.setting_panel.entries[x].call_on_change = self.on_display_change


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

    def on_display_change(self, force_update=False):
        update_window = self.app.update_display_settings(force_update)

        if update_window:
            self.app.change_scene(SettingsScene(self.app, self.setting_panel.scroll_offset))  # Reload settings scene
