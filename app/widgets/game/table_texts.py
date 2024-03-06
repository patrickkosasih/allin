import pygame.sprite

from app.animations.anim_group import AnimGroup
from app.animations.var_slider import VarSlider
from app.animations.move import MoveAnimation
from app.animations.interpolations import *

from app.shared import *
from app.widgets.widget import Widget, WidgetComponent


class TableText(Widget):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args)
        self.layer = Layer.TABLE_TEXT

        """
        Components
        """
        self.component_group = pygame.sprite.Group()
        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        self.text = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")

        self.text_str = ""
        self.visible = True

        self.anim_group = AnimGroup()

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

    def set_visible(self, visible: bool, duration: float = 0.25):
        if self.visible == visible:
            return

        if duration > 0:
            animation = VarSlider(duration, 255 * self.visible, 255 * visible,
                                  setter_func=lambda x: self.image.set_alpha(int(x)))
            self.anim_group.add(animation)
        else:
            self.image.set_alpha(255 * visible)

        self.visible = visible

    def update(self, dt):
        self.anim_group.update(dt)
        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)


class PotText(TableText):
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
        self.anim_group.add(animation)

        self.pot = pot


class RankingText(TableText):
    def __init__(self, *rect_args, **kwargs):
        super().__init__(*rect_args, **kwargs)

    def set_text_anim(self, text_str: str):
        if text_str == self.text_str:
            return

        _, _, w, h = self.rect
        self.text.move_anim(0.25, (0, 100), "%", "ctr", "ctr",
                            interpolation=ease_in, call_on_finish=lambda: self.__set_text_anim2(text_str))

    def __set_text_anim2(self, text_str: str):
        """
        The continuation of the `set_text_anim` method that is called when the first animation is finished.
        """

        self.set_text(text_str, set_rect=False)

        _, _, w, h = self.rect
        self.text.move_anim(0.25, (0, 0), "%", "ctr", "ctr",
                            start_pos=(0, -100), interpolation=ease_out)
