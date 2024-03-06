import pygame

import rules.game_flow
import rules.basic
from app.shared import *

from app.animations.anim_group import AnimGroup
from app.animations.var_slider import VarSlider
from app.animations.interpolations import ease_out
from app.widgets.widget import Widget, WidgetComponent

DEFAULT_HEAD_COLOR = 95, 201, 123
DEFAULT_SUB_COLOR = 32, 46, 38
DEFAULT_TEXT_COLOR = 255, 255, 255

class ComponentCodes:
    """
    The `Component` class contains constants (codes) to reference components on the `component` dict of the
    `PlayerDisplay` class. Each component of a player display is assigned an integer code from 0 to 5. The drawing order
    of every component is based on their respective codes.
    """

    # Sub
    SUB_BASE = 0
    SUB_TEXT = 1

    # Head
    HEAD_BASE = 2
    NAME_TEXT = 3
    MONEY_TEXT = 4
    PROFILE_PIC = 5


class PlayerDisplay(Widget):
    """
    The `PlayerDisplay` class is the GUI representation of a player. Each player display has two main parts: the head
    and the sub. The head has 4 components, while the sub has 2 components.

    I. Head
        1. Head base
        2. Name text
        3. Money text
        4. Profile picture

    II. Sub
        1. Sub base
        2. Sub text

    Apart from the components above, there are sprites that are placed based on the position of a player display, but
    are actually not part of the player display sprite:

    1. Two pocket cards
    2. Winner crown
    """

    def __init__(self, parent, *rect_args, player_data: rules.game_flow.Player):
        super().__init__(parent, *rect_args)
        self.layer = Layer.PLAYER

        """
        Player display components
        """
        self.components = {}

        self.pocket_cards = pygame.sprite.Group()
        # Note: Pocket cards are separate from player displays.

        """
        Data fields
        """
        self.player_data: rules.game_flow.Player = player_data

        self.sub_text_str = ""
        self.sub_pos: float = 0
        """`sub_pos` determines the current position of the sub. 0 being retracted (hidden behind the head), and 1 being
        extended (placed right below the head)."""

        self.money_text_val: int = self.player_data.money

        self.init_components()

    def init_components(self):
        """
        Initialize all the 6 components of the player display.

        Each component is put into the `self.components` dict and added to the `self.component_group` sprite group.
        """
        for i in range(6):
            self.components[i] = WidgetComponent(self, 0, 0, 0, 0)
            self.redraw_component(i)
            self.component_group.add(self.components[i])

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)

    def redraw_component(self, component_code: int):
        # TODO Code the player display's component system from scratch

        if not 0 <= component_code <= 5:
            raise ValueError(f"component_code must be a constant from the Component class, got: {component_code}")

        w, h = self.rect.width, self.rect.height
        w_head, h_head = w, 0.7 * h
        w_sub, h_sub = 0.8 * w, 0.3 * h

        component: WidgetComponent = self.components[component_code]

        match component_code:
            case ComponentCodes.SUB_BASE:
                component.image = pygame.Surface((w_sub, h_sub), pygame.SRCALPHA)
                draw_rounded_rect(component.image, pygame.Rect(0, 0, w_sub, h_sub), color=DEFAULT_SUB_COLOR)
                component.image.set_alpha(150)

            case ComponentCodes.SUB_TEXT:
                component.image = FontSave.get_font(3).render(self.sub_text_str, True, DEFAULT_TEXT_COLOR)

            case ComponentCodes.HEAD_BASE:
                component.image = pygame.Surface((w_head, h_head), pygame.SRCALPHA)
                component.rect = component.image.get_rect(center=(w / 2, h_head / 2))

                draw_rounded_rect(component.image, pygame.Rect(0, 0, w_head, h_head), color=DEFAULT_HEAD_COLOR, b=0)

            case ComponentCodes.NAME_TEXT:
                component.image = FontSave.get_font(3.5).render(self.player_data.name, True, DEFAULT_TEXT_COLOR)
                component.rect = component.image.get_rect(center=((w + h_head / 2) / 2, 0.25 * h_head))

            case ComponentCodes.MONEY_TEXT:
                component.image = FontSave.get_font(3.5).render(f"${self.money_text_val:,}", True, DEFAULT_TEXT_COLOR)
                component.rect = component.image.get_rect(center=((w + h_head / 2) / 2, 0.75 * h_head))

            case ComponentCodes.PROFILE_PIC:
                r = int(h_head / 2)

                component.image = pygame.Surface((h_head, h_head), pygame.SRCALPHA)
                component.rect = component.image.get_rect(center=(r, r))

                # Profile pictures are currently circles with a random solid color
                color = rand_color()
                pygame.gfxdraw.aacircle(component.image, r, r, r, color)
                pygame.gfxdraw.filled_circle(component.image, r, r, r, color)

        # Sub base and sub text positioning
        if component_code in (ComponentCodes.SUB_BASE, ComponentCodes.SUB_TEXT):
            component.rect = component.image.get_rect(center=(w / 2, h_head - h_sub / 2 + self.sub_pos * h_sub))

    def set_sub_text_anim(self, new_text: str):
        """
        Set the sub text with an animation.

        :param new_text: The new text.
        """

        extended = self.sub_pos >= 0.5

        if new_text == self.sub_text_str and extended:  # Old text == New text
            return

        elif new_text and extended:  # Old text -> New text
            animation = VarSlider(duration=0.1, start_val=1, end_val=0, setter_func=self.set_sub_pos,
                                  call_on_finish=lambda: self.set_sub_text_anim(new_text))

        elif new_text and not extended:  # Nothing -> New text
            self.set_sub_text(new_text)
            animation = VarSlider(duration=0.25, start_val=0, end_val=1, setter_func=self.set_sub_pos)

        elif not new_text and extended:  # Old text -> Nothing
            animation = VarSlider(duration=0.25, start_val=1, end_val=0, setter_func=self.set_sub_pos)

        else:  # Nothing -> Nothing
            return

        self.anim_group.add(animation)

    def set_sub_text(self, new_text: str):
        """
        Directly change the sub text.
        """
        self.sub_text_str = new_text
        self.redraw_component(ComponentCodes.SUB_TEXT)

    def set_sub_pos(self, sub_pos):
        self.sub_pos = sub_pos
        self.redraw_component(ComponentCodes.SUB_BASE)
        self.redraw_component(ComponentCodes.SUB_TEXT)

    def set_money_text(self, money: int or float):
        self.money_text_val = int(money)
        self.redraw_component(ComponentCodes.MONEY_TEXT)

    def update_money(self, duration=0.5):
        old_money, new_money = self.money_text_val, self.player_data.money

        if duration > 0:
            animation = VarSlider(duration, old_money, new_money, setter_func=self.set_money_text,
                                  interpolation=lambda x: ease_out(x, 3))
            self.anim_group.add(animation)

        else:
            self.set_money_text(new_money)


    def update(self, dt):
        if self.anim_group.animations:
            # Only update image if there is an animation.
            self.anim_group.update(dt)
            self.image.fill((0, 0, 0, 0))
            self.component_group.draw(self.image)

    """
    Component getters using property
    """
    sub_base = property(lambda self: self.components[ComponentCodes.SUB_BASE])
    sub_text = property(lambda self: self.components[ComponentCodes.SUB_TEXT])
    head_base = property(lambda self: self.components[ComponentCodes.HEAD_BASE])
    name_text = property(lambda self: self.components[ComponentCodes.NAME_TEXT])
    money_text = property(lambda self: self.components[ComponentCodes.MONEY_TEXT])
    profile_pic = property(lambda self: self.components[ComponentCodes.PROFILE_PIC])
