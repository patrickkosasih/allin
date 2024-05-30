import pygame

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

        """
        Setting panel
        
        1. Audio
            * Music volume
            * SFX volume
        
        2. Graphics
            * Windowed
            * Window resolution
            * FPS limit
        
        3. Interface
            * Start-up sequence
            * Background
        """
        self.setting_panel = SettingPanel(self, 0, 0, 75, 75, "%", "ctr", "ctr",
                                          base_color=(24, 31, 37, 200),
                                          base_radius=5, pack_height=12, entry_horizontal_margin=3)

        self.setting_panel.add_header("Settings")

        # region Audio
        self.setting_panel.add_header("Audio", font_scale=0.75)

        self.setting_panel.add_entry("music_volume", "Music Volume").set_input_widget(
            SettingEntry.SLIDER
        )

        self.setting_panel.add_entry("sfx_volume", "SFX Volume").set_input_widget(
            SettingEntry.SLIDER
        )
        # endregion

        # region Graphics
        self.setting_panel.add_header("Graphics", font_scale=0.75)

        self.setting_panel.add_entry("windowed", "Windowed").set_input_widget(
            SettingEntry.TOGGLE_SWITCH
        )

        self.setting_panel.add_entry("window_resolution", "Window Resolution").set_input_widget(
            SettingEntry.ITEM_PICKER, items=[(800, 600), (1280, 720), (1366, 768), (1920, 1080)],
            format_func=lambda x: f"{x[0]} × {x[1]}"
        )

        self.setting_panel.add_entry("fps_limit", "FPS Limit").set_input_widget(
            SettingEntry.ITEM_PICKER, items=[0, 30, 45, 60, 90, 120, 144, 240], default_index=3,
            format_func=lambda x: "Unlimited" if x == 0 else str(x)
        )
        # endregion

        # region Interface
        self.setting_panel.add_header("Interface", font_scale=0.75)

        self.setting_panel.add_entry("show_startup_sequence", "Show Start-up Sequence").set_input_widget(
            SettingEntry.TOGGLE_SWITCH, default_state=True
        )

        self.setting_panel.add_entry("background", "Background").set_input_widget(
            SettingEntry.TOGGLE_SWITCH, default_state=True
        )
        # endregion

        """
        Buttons
        """
        self.back_button = CircularButton(self, 1.5, 1.5, 4, "%h", "tl", "tl",
                                          command=self.back,
                                          icon=load_image("assets/sprites/menu icons/back.png"),
                                          icon_size=0.8)

    def back(self):
        self.app.change_scene_anim("mainmenu")
