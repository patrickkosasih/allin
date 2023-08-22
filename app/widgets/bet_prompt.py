import pygame.sprite

from app.widgets.action_buttons import ActionButton, COLORS
from app.widgets.button import Button
from app.widgets.slider import Slider
from app.shared import *

from rules.game_flow import Actions, Player


class BetPrompt(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions, player):
        super().__init__()

        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.player = player

        """
        Components
        """
        self.component_group = pygame.sprite.Group()
        global_x, global_y, w, h = self.rect

        # Slider
        self.slider = BetSlider((w / 2, h / 6), (w, h / 3), self)
        self.slider.global_rect.x += global_x
        self.slider.global_rect.y += global_y

        self.component_group.add(self.slider)

        # Confirm button
        self.confirm_button = BetConfirmButton((w - w/4, h - h/4), (w/2, h/2), self)
        self.confirm_button.global_rect.x += global_x
        self.confirm_button.global_rect.y += global_y

        self.component_group.add(self.confirm_button)

        # Edit button
        self.edit_button = BetEditButton((2/5 * w, h - h/4), h/4, self)
        self.edit_button.global_rect.x += global_x
        self.edit_button.global_rect.y += global_y

        self.component_group.add(self.edit_button)

    def update(self, dt):
        self.component_group.update(dt)

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)


class BetSlider(Slider):
    def __init__(self, pos, dimensions, prompt: BetPrompt, **kwargs):
        super().__init__(pos, dimensions, **kwargs)
        self.prompt = prompt


class BetConfirmButton(ActionButton):
    def __init__(self, pos, dimensions, prompt: BetPrompt, **kwargs):
        super().__init__(pos, dimensions, prompt.player, color=COLORS["raise"], text_str="Bet $727|", **kwargs)

    def on_click(self):
        pass

    def update_bet_amount(self, new_bet_amount: int):
        pass


class BetEditButton(Button):
    def __init__(self, pos, radius, prompt: BetPrompt):
        super().__init__(pos, (2 * radius, 2 * radius),
                         color=hsv_factor(COLORS["raise"], sf=1.1, vf=0.8),
                         icon=pygame.image.load("assets/sprites/action icons/edit bet.png"))

        self.prompt = prompt

    def draw_base(self):
        """
        Draw a circle for the button base instead of a rounded rectangle.
        """
        # Overridden from:
        # draw_rounded_rect(self.base.image, self.base.rect, self.color, self.b_color, self.b_thickness)

        r = int(self.rect.h / 2)
        pygame.gfxdraw.aacircle(self.base.image, r, r, r, self.color)
        pygame.gfxdraw.filled_circle(self.base.image, r, r, r, self.color)
