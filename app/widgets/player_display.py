import random
import pygame

import rules.game_flow
import rules.basic
from app.shared import *
from testing import func_timer


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


class PlayerDisplay(pygame.sprite.Sprite):
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
    """

    def __init__(self, pos, dimensions, player_data: rules.game_flow.Player):
        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.layer = Layer.PLAYER

        """
        Player display components
        """
        self.components = {}
        self.component_group = pygame.sprite.Group()

        """
        Data fields
        """
        self.player_data = player_data
        self.sub_text_str = ""

        self.init_components()


    def init_components(self):
        """
        Initialize all the 6 components of the player display.

        Each component is put into the `self.components` dict and added to the `self.component_group` sprite group.
        """
        for i in range(6):
            self.components[i] = pygame.sprite.Sprite()
            self.redraw_component(i)
            self.component_group.add(self.components[i])

    def redraw_component(self, component_code: int):
        if not 0 <= component_code <= 5:
            raise ValueError(f"component_code must be a constant from the Component class, got: {component_code}")

        w, h = self.rect.width, self.rect.height
        w_head, h_head = w, 0.7 * h
        w_sub, h_sub = 0.8 * w, 0.3 * h

        component = self.components[component_code]

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
                component.image = FontSave.get_font(3.5).render(f"${self.player_data.money:,}", True, DEFAULT_TEXT_COLOR)
                component.rect = component.image.get_rect(center=((w + h_head / 2) / 2, 0.75 * h_head))

            case ComponentCodes.PROFILE_PIC:
                r = int(h_head / 2)

                component.image = pygame.Surface((h_head, h_head), pygame.SRCALPHA)
                component.rect = component.image.get_rect(center=(r, r))

                # Profile pictures are currently circles with a random solid color
                color = rand_color()
                pygame.gfxdraw.aacircle(component.image, r, r, r, color)
                pygame.gfxdraw.filled_circle(component.image, r, r, r, color)

        if component_code in (ComponentCodes.SUB_BASE, ComponentCodes.SUB_TEXT):
            component.rect = component.image.get_rect(center=(w / 2, h_head + h_sub / 2))

    def set_sub_text(self, text: str):
        self.sub_text_str = text
        self.redraw_component(ComponentCodes.SUB_TEXT)

    def update_money(self):
        self.redraw_component(ComponentCodes.MONEY_TEXT)

    def update(self, dt):
        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)
