import pygame.sprite

from app.animations.anim_group import AnimGroup
from app.animations.interpolations import ease_in, ease_out
from app.animations.move import MoveAnimation
from app.widgets.game.action_buttons import COLORS, SideTextedButton
from app.widgets.button import Button
from app.widgets.slider import Slider
from app.shared import *
from app.widgets.widget import Widget

from rules.game_flow import Actions


class BetPrompt(Widget):
    def __init__(self, parent, *rect_args, game_scene, player):
        super().__init__(parent, *rect_args)

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
        self.slider = BetSlider(self, 0, 0, 100, 30, "%", "mt", "mt")
        self.confirm_button = BetConfirmButton(self, 0, 0, 50, 50, "%", "br", "br")
        self.edit_button = BetEditButton(self, -2, 0, 50 / self.rect.aspect_ratio, 50, "%", "mb", "br")

        """
        Show/hide related attributes
        """
        self.shown = False
        self.anim_group = AnimGroup()

        self.original_pos = self.rect.center
        self.hidden_pos = Vector2(self.original_pos) + Vector2(0, 1.2 * self.rect.height)

    def set_bet(self, bet):
        self.bet_amount = bet
        self.confirm_button.update_bet_text()

    def set_shown(self, shown: bool, duration=0.4):
        self.shown = shown

        if shown:
            self.slider.update_range()
            self.confirm_button.update_bet_text()

        if duration > 0:
            animation = MoveAnimation(duration, self, None, self.original_pos if shown else self.hidden_pos,
                                      "px", "tl", "ctr",
                                      interpolation=ease_out if shown else ease_in)
            self.anim_group.add(animation)

        else:
            self.rect.set_pos(*(self.original_pos if shown else self.hidden_pos), "px", "tl", "ctr")

    def set_edit_mode(self, edit_mode):
        self.edit_mode = edit_mode

        if edit_mode:
            self.edit_button.set_icon(pygame.image.load("assets/sprites/action icons/cancel.png"), 0.9)
            self.confirm_button.current_bet_input = self.bet_amount
            self.confirm_button.set_side_text_money(0)
            self.confirm_button.all_in = False

        else:
            self.edit_button.set_icon(pygame.image.load("assets/sprites/action icons/edit bet.png"))

            new_bet = self.confirm_button.current_bet_input
            new_bet = max(self.slider.min_value, min(new_bet, self.slider.max_value))
            self.set_bet(new_bet)
            self.slider.set_value(new_bet, update_thumb_pos=True)

            self.confirm_button.blink = False
            self.confirm_button.update_bet_text()

    def update(self, dt):
        super().update(dt)


class BetSlider(Slider):
    def __init__(self, prompt, *rect, **kwargs):
        super().__init__(prompt, *rect, int_only=True, **kwargs)
        self.prompt = prompt

    def on_change(self):
        self.prompt.set_bet(self.current_value)

    def update_range(self):
        current_bet = self.prompt.game_scene.game.deal.bet_amount
        min_bet = self.prompt.game_scene.game.min_bet

        self.min_value = 2 * current_bet if current_bet else min_bet
        self.max_value = self.prompt.player.money + self.prompt.player.player_hand.bet_amount

        self.min_value = min(self.min_value, self.max_value)

        self.set_value(self.min_value, update_thumb_pos=True)
        self.on_change()


class BetConfirmButton(SideTextedButton):
    def __init__(self, prompt, *rect_args, **kwargs):
        super().__init__(prompt, *rect_args,
                         color=COLORS["raise"], text_str="", command=self.on_click,
                         icon=pygame.image.load("assets/sprites/action icons/confirm bet.png"), icon_size=0.8,
                         **kwargs)

        self.prompt = prompt

        self.current_bet_input = 0
        self.blink_timer = 0
        self.blink = False

        KeyBroadcaster.add_listener(self.key_down)

    def on_click(self):
        bet_result = self.prompt.player.action(Actions.BET, self.prompt.bet_amount)
        if bet_result == 0:
            self.prompt.set_shown(False)

    def key_down(self, event):
        if not self.prompt.edit_mode:
            return

        elif event.unicode.isnumeric():
            self.current_bet_input *= 10
            self.current_bet_input += int(event.unicode)

        elif event.key == pygame.K_BACKSPACE:
            self.current_bet_input //= 10

        elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.prompt.set_edit_mode(False)

    def update_bet_text(self):
        if self.prompt.edit_mode:
            self.set_text((f"${self.current_bet_input:,}" if self.current_bet_input > 0 else "$") +
                          ('|' if self.blink else ''))
        else:
            self.set_text(f"${self.prompt.bet_amount:,}")

            amount_to_pay = self.prompt.bet_amount - self.prompt.player.player_hand.bet_amount
            self.all_in = amount_to_pay >= self.prompt.player.money

            if self.prompt.player.player_hand.bet_amount > 0:
                self.set_side_text_money(amount_to_pay)
            else:
                self.set_side_text_money(0)

    def update(self, dt):
        if self.prompt.edit_mode:
            # Blink cursor
            self.blink_timer += dt

            if self.blink_timer >= 0.5:
                self.blink = not self.blink
                self.blink_timer = 0

            self.update_bet_text()

        super().update(dt)


class BetEditButton(Button):
    def __init__(self, prompt, *rect_args):
        super().__init__(prompt, *rect_args,
                         command=self.on_click,
                         color=hsv_factor(COLORS["raise"], sf=0.9, vf=1.2),
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
        self.prompt.set_edit_mode(not self.prompt.edit_mode)

    def update(self, dt):
        super().update(dt)
        if self.prompt.edit_mode and pygame.mouse.get_pressed()[0] and not self.hover:
            self.prompt.set_edit_mode(False)
