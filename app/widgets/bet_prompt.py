import pygame.sprite

from app.widgets.action_buttons import COLORS
from app.widgets.button import Button
from app.widgets.slider import Slider
from app.shared import *

from rules.game_flow import Actions


class BetPrompt(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions, game_scene, player):
        super().__init__()

        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.game_scene = game_scene
        self.player = player

        """
        Data fields
        """
        self.bet_amount = 100
        self.edit_mode = False

        """
        Components
        """
        # region Components
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
        # endregion

    def set_bet(self, bet):
        self.bet_amount = bet
        self.confirm_button.update_bet_text()

    def update(self, dt):
        self.component_group.update(dt)

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)


class BetSlider(Slider):
    def __init__(self, pos, dimensions, prompt: BetPrompt, **kwargs):
        super().__init__(pos, dimensions, **kwargs)
        self.prompt = prompt

    def on_change(self):
        self.prompt.set_bet(int(self.current_value))

    def update_range(self):
        current_bet = self.prompt.game_scene.game.deal.bet_amount
        min_bet = self.prompt.game_scene.game.min_bet

        self.min_value = 2 * current_bet if current_bet else min_bet
        self.max_value = self.prompt.player.money
        self.set_value(min(self.min_value, max(self.max_value, self.prompt.bet_amount)),
                       update_thumb_pos=True)


class BetConfirmButton(Button):
    def __init__(self, pos, dimensions, prompt: BetPrompt, **kwargs):
        super().__init__(pos, dimensions, color=COLORS["raise"], text_str="", **kwargs)

        self.prompt = prompt
        self.blink_timer = 0
        self.blink = False

    def on_click(self):
        self.prompt.player.action(Actions.BET, self.prompt.bet_amount)

    def update_bet_text(self):
        self.set_text(f"${self.prompt.bet_amount:,}{'|' if self.blink else ''}")

    def edit_mode_update(self, dt):
        """
        The method that is called every game tick when the bet prompt is currently set to edit mode.
        """
        # Blink cursor
        self.blink_timer += dt

        if self.blink_timer >= 0.5:
            self.blink = not self.blink
            self.blink_timer = 0

        self.update_bet_text()

        # if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        #     self.prompt.bet_amount += 1

    def update(self, dt):
        if self.prompt.edit_mode:
            self.edit_mode_update(dt)

        elif self.blink:
            self.update_bet_text()

        super().update(dt)


class BetEditButton(Button):
    def __init__(self, pos, radius, prompt: BetPrompt):
        super().__init__(pos, (2 * radius, 2 * radius),
                         command=self.on_click,
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

    def on_click(self):
        self.prompt.edit_mode = not self.prompt.edit_mode

    def update(self, dt):
        super().update(dt)
        if pygame.mouse.get_pressed()[0] and not self.hover:
            self.prompt.edit_mode = False
