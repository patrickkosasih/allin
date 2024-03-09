from app.scenes.scene import Scene
from app.widgets.basic.panel import Panel


class SingleplayerMenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)

        self.setting_panel = Panel(self, 0, 0, 75, 75, "%", "ctr", "ctr")
