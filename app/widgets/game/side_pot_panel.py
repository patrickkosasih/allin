from typing import TYPE_CHECKING

import pygame

from app.animations.interpolations import ease_out
from app.animations.var_slider import VarSlider
from app.shared import FontSave, Layer
from app.tools.draw import draw_rounded_rect
from app.widgets.basic.panel import Panel
from app.widgets.widget import Widget, WidgetComponent
from rules.game_flow import PokerGame

if TYPE_CHECKING:
    from app.scenes.game_scene import GameScene

DEFAULT_COLOR = (255, 255, 255)


class SidePotText(Widget):
    def __init__(self, parent: "SidePotPanel", *rect_args, pot_name_str: str, shown=True):
        super().__init__(parent, *rect_args)

        self.pot_value = -1
        self.shown = True

        """
        Texts
        """
        self.font = FontSave.get_font(self.rect.h * 0.8, "px")

        self.pot_name_text = WidgetComponent(self, 0, 0, 0, 0, "px", "ml", "ml")
        self.pot_name_text.image = self.font.render(pot_name_str, True, DEFAULT_COLOR)

        self.pot_value_text = WidgetComponent(self, 0, 0, 0, 0, "px", "mr", "mr")

        self.set_pot_value(0)
        self.set_shown(shown)

    def set_pot_value(self, value: int, update_field=True):
        if update_field:
            self.pot_value = value

        self.pot_value_text.image = self.font.render(f"${value:,}", True, DEFAULT_COLOR)
        self.pot_value_text.set_pos(0, 0, "px", "mr", "mr")

    def set_pot_value_anim(self, value: int, duration=0.4):
        if self.pot_value == value:
            return
        elif not self.parent.shown:
            self.set_pot_value(value)
            return

        animation = VarSlider(duration, self.pot_value, value,
                              setter_func=lambda x: self.set_pot_value(int(x), False),
                              interpolation=lambda x: ease_out(x, 3))
        self.scene.anim_group.add(animation)
        self.pot_value = value

    def set_shown(self, shown: bool, duration=0.5):
        if self.shown != shown:
            self.shown = shown
            if self.parent.shown and duration > 0:
                self.fade_anim(duration, 255 if shown else 0)
            else:
                self.image.set_alpha(255 if shown else 0)

    def update(self, dt):
        if self.image.get_alpha() != 0:
            super().update(dt)


class SidePotPanel(Panel):
    def __init__(self, parent, *rect_args, game: PokerGame):
        super().__init__(parent, base_radius=10, pack_height=15, outer_margin=8, *rect_args)
        self.layer = Layer.SIDE_MENU

        self.shown = True
        self.game = game

        """
        Current round bets text.
        """
        self._current_bets_text = SidePotText(self, *self.next_pack_rect, pot_name_str="Current Round Bets")
        self.add_scrollable(self._current_bets_text)

        """
        Line separator between the current bets and the pots.
        """
        self._line_separator = WidgetComponent(self, *self.next_pack_rect)

        th = self._line_separator.rect.h * 0.005
        draw_rounded_rect(self._line_separator.image,
                          pygame.Rect(0, self._line_separator.rect.h / 2 - th / 2, self._line_separator.rect.w, th),
                          DEFAULT_COLOR)

        self.add_scrollable(self._line_separator)

        """
        Side pot (and main pot) texts
        """
        self._side_pot_texts = []
        for i in range(10):
            side_pot_text = SidePotText(self, *self.next_pack_rect,
                                        pot_name_str=f"Side Pot {i}" if i > 0 else "Main Pot")
            self.add_scrollable(side_pot_text)
            self._side_pot_texts.append(side_pot_text)

        self.reset_all_pots()

    def set_shown(self, shown: bool, duration=0.5):
        if self.shown != shown:
            self.shown = shown
            if duration > 0:
                self.fade_anim(duration, 255 if shown else 0)
            else:
                self.image.set_alpha(255 if shown else 0)

    def on_mouse_down(self, event):
        if self.shown:
            super().on_mouse_down(event)

            if not self.hover:
                self.parent: GameScene
                self.parent.show_side_pot_panel(False)

    def update_current_bets(self):
        self._current_bets_text.set_pot_value_anim(self.game.hand.current_round_bets)

    def update_all_pots(self):
        self.update_current_bets()

        for side_pot_text, pot_value in zip(self._side_pot_texts, self.game.hand.pots):
            side_pot_text.set_pot_value_anim(pot_value)

            if not side_pot_text.shown and pot_value > 0:
                side_pot_text.set_shown(True)
                bottommost_text = self._side_pot_texts[len(self.game.hand.pots) - 1]
                self._scroll_min = self.rect.h - bottommost_text.rect.top - self._outer_margin

    def reset_all_pots(self):
        self._scroll_min = 0
        
        for x in self._side_pot_texts:
            x.set_pot_value_anim(0)
            x.set_shown(False)

    def update(self, dt):
        if self.image.get_alpha() != 0:
            super().update(dt)
