import pygame.image

from app.scenes.game_scene import GameScene
from app.scenes.scene import Scene
from app.shared import FontSave
from app.widgets.basic.button import Button, CircularButton
from app.widgets.basic.number_picker import NumberPicker
from app.widgets.menu.form_panel import FormPanel, FormEntry
from rules.singleplayer import SingleplayerGame


class SingleplayerMenuScene(Scene):
    def __init__(self, app):
        super().__init__(app, "singleplayer")

        """
        Setting panel
        """
        self.setting_panel = FormPanel(self, 0, -5, 75, 65, "%", "ctr", "ctr",
                                       base_color=(24, 31, 37, 128),
                                       base_radius=5, pack_height=12, entry_horizontal_margin=3)

        # Setting panel elements
        self.setting_panel.add_header("Singleplayer Game")

        self.setting_panel.add_entry("n_bots", "Number of Bots").set_input_widget(
            FormEntry.NUMBER_PICKER, min_value=1, max_value=9, default_value=5
        )

        self.setting_panel.add_entry("starting_money", "Starting Money").set_input_widget(
            FormEntry.NUMBER_PICKER, min_value=500, max_value=10000, default_value=1000, step=500,
            format_func=lambda x: f"${x:,}"
        )

        self.setting_panel.add_entry("sb_amount", "Blinds Amount").set_input_widget(
            FormEntry.NUMBER_PICKER, min_value=5, max_value=250, default_value=25, step=5,
            format_func=lambda x: f"${x:,} / ${x * 2:,}"
        )

        """
        Buttons
        """
        self.start_button = Button(self, 37.5, 37.5, 20, 8, "%", "ctr", "br",
                                   text_str="Start Game", command=self.start,
                                   font=FontSave.get_font(6), color=(126, 237, 139),
                                   icon=pygame.image.load("assets/sprites/action icons/confirm bet.png"),
                                   icon_size=0.8, icon_align="right")

        self.back_button = CircularButton(self, 1.5, 1.5, 4, "%h", "tl", "tl",
                                          command=self.back,
                                          icon=pygame.image.load("assets/sprites/menu icons/back.png"),
                                          icon_size=0.8)

    def start(self):
        game_settings = self.setting_panel.get_form_data()
        self.app.change_scene_anim(lambda: GameScene(self.app, SingleplayerGame(**game_settings)), duration=0.5)
        # FIXME Prevent the player from spamming the start button while the scene is fading.

    def back(self):
        self.app.change_scene_anim("mainmenu")

    def broadcast_keyboard(self, event: pygame.event.Event):
        super().broadcast_keyboard(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()
