from app.scenes.scene import Scene
from app.widgets.menu.form_panel import FormPanel


class SingleplayerMenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)

        self.setting_panel = FormPanel(self, 0, 0, 75, 75, "%", "ctr", "ctr",
                                       base_color=(24, 31, 37, 128), base_radius=5)

        self.setting_panel.add_entry("Number of Bots")
        self.setting_panel.add_entry("Starting Money")
        self.setting_panel.add_entry("Blinds Amount")

        for i in range(30):
            self.setting_panel.add_entry("Hey" + "." * i)
