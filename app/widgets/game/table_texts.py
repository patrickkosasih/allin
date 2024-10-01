from typing import TYPE_CHECKING

import pygame.sprite

from app.animations.var_slider import VarSlider
from app.animations.interpolations import *

from app.shared import *
from app.tools import app_timer
from app.widgets.listeners import MouseListener
from app.widgets.widget import Widget, WidgetComponent

if TYPE_CHECKING:
    from app.scenes.game_scene import GameScene

class TableText(Widget):
    def __init__(self, parent: "GameScene", *rect_args):
        super().__init__(parent, *rect_args)
        self.layer = Layer.TABLE_TEXT

        """
        Components
        """
        self.component_group = pygame.sprite.Group()
        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        self.text = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")

        self.text_str = ""
        self.shown = True

        """
        Initialize
        """
        self.draw_base()
        self.set_text("")

    def draw_base(self):
        """
        Initialize the components of a table text widget: the base and the text.
        """

        draw_rounded_rect(self.base.image, self.base.rect, (0, 0, 0))
        self.base.image.set_alpha(100)

    def set_text(self, text_str: str, set_rect=True):
        self.text_str = text_str
        self.text.image = FontSave.get_font(3.5).render(text_str, True, "white")
        if set_rect:
            self.text.rect = self.text.image.get_rect(center=(self.rect.width / 2, self.rect.height / 2))

    def set_shown(self, visible: bool, duration: float = 0.25):
        if self.shown == visible:
            return

        if duration > 0:
            animation = VarSlider(duration, 255 * self.shown, 255 * visible,
                                  setter_func=lambda x: self.image.set_alpha(int(x)))
            self.scene.anim_group.add(animation)
        else:
            self.image.set_alpha(255 * visible)

        self.shown = visible

    def update(self, dt):
        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)


class PotText(TableText, MouseListener):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)

        self.pot = 0
        self.set_text("$0")

        """
        "Pot:" label
        """
        m = self.rect.height / 2
        label = FontSave.get_font(3).render("Pot:", True, (150, 150, 150))
        label_rect = label.get_rect(midleft=(m, m))
        self.base.image.blit(label, label_rect)

    def set_text_anim(self, pot: int):
        animation = VarSlider(0.4, self.pot, pot,
                              setter_func=lambda x: self.set_text(f"${int(x):,}"),
                              interpolation=lambda x: ease_out(x, 3))
        self.scene.anim_group.add(animation)

        self.pot = pot

    def on_click(self, event):
        if self.shown:
            self.parent: "GameScene"
            self.parent.show_side_pot_panel(True)

    def update(self, dt):
        super().update(dt)

        if self.hover:
            if self.mouse_down:
                self.image.fill((30, 30, 30), special_flags=pygame.BLEND_SUB)
            else:
                self.image.fill((30, 30, 30), special_flags=pygame.BLEND_ADD)


class RankingText(TableText):
    def __init__(self, *rect_args, **kwargs):
        super().__init__(*rect_args, **kwargs)

    def set_text_anim(self, text_str: str, duration=0.25):
        if text_str == self.text_str:
            return

        app_timer.Sequence([
            lambda: self.text.move_anim(duration, (0, 100), "%", "ctr", "ctr",
                                interpolation=ease_in),
            duration,

            lambda: self.set_text(text_str, set_rect=False),
            lambda: self.text.move_anim(duration, (0, 0), "%", "ctr", "ctr",
                                start_pos=(0, -100), interpolation=ease_out),
        ])
