import pygame.sprite

from app.animations.anim_group import AnimGroup
from app.animations.var_slider import VarSlider
from app.animations.move import MoveAnimation
from app.animations.interpolations import *

from app.shared import *


class TableText(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions):
        super().__init__()

        """
        Sprite attributes
        """
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.layer = Layer.TABLE_TEXT

        """
        Components
        """
        self.component_group = pygame.sprite.Group()
        self.base = pygame.sprite.Sprite(self.component_group)
        self.text = pygame.sprite.Sprite(self.component_group)

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

        self.base.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.base.rect = self.base.image.get_rect(topleft=(0, 0))

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
    def __init__(self, pos, dimensions):
        super().__init__(pos, dimensions)

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
    def __init__(self, pos, dimensions):
        super().__init__(pos, dimensions)

    def set_text_anim(self, text_str: str):
        if text_str == self.text_str:
            return

        _, _, w, h = self.rect
        animation = MoveAnimation(0.25, self.text, None, (w / 2, 3 * h / 2), interpolation=ease_in,
                                  call_on_finish=lambda: self.__set_text_anim2(text_str))
        self.anim_group.add(animation)

    def __set_text_anim2(self, text_str: str):
        """
        The continuation of the `set_text_anim` method that is called when the first animation is finished.
        """

        self.set_text(text_str, set_rect=False)

        _, _, w, h = self.rect
        animation = MoveAnimation(0.25, self.text,(w / 2, -h / 2) , (w / 2, h / 2), interpolation=ease_out)
        self.anim_group.add(animation)
