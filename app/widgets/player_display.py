import random
import pygame

import rules.game_flow
import rules.basic
from app.shared import *
from testing import func_timer


DEFAULT_HEAD_COLOR = 95, 201, 123
DEFAULT_SUB_COLOR = 32, 46, 38
DEFAULT_TEXT_COLOR = 255, 255, 255

class Component:
    """
    The `Component` class contains constants to reference components on the `component` dict of a `PlayerDisplay`
    object. A component constant is an integer from 0 to 5, and every component is drawn in order of their numbers.
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
    The `PlayerDisplay` class is the GUI representation of a player. A single player display has two group of
    components: the head and the sub. The head has 4 components, while the sub has 2 components.

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

        w, h = self.rect.width, self.rect.height
        w_head, h_head = w, 0.7 * h
        w_sub, h_sub = 0.8 * w, 0.3 * h

        self.head = pygame.Surface((w_head, h_head), pygame.SRCALPHA)
        self.head_rect = self.head.get_rect(center=(w / 2, h_head / 2))

        self.sub = pygame.Surface((w_sub, h_sub), pygame.SRCALPHA)
        self.sub_rect = self.sub.get_rect(center=(w / 2, h_head + h_sub / 2))

        # TODO: Move every component of the player display into a dictionary and group, which are fields of the class.
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

    def draw_head(self):
        """
        Draw the head frame.
        """
        _, _, w, h = self.head_rect
        r = h / 2

        """
        1. Head frame base
        """
        draw_rounded_rect(self.head, pygame.Rect(0, 0, w, h), color=DEFAULT_HEAD_COLOR, b=0)

        """
        2. Player name text
        """
        name_text = pygame.sprite.Sprite()
        name_text.image = FontSave.get_font(3.5).render(self.player_data.name, True, DEFAULT_TEXT_COLOR)
        name_text.rect = name_text.image.get_rect(center=((w + r) / 2, 0.25 * h))

        group_thing = pygame.sprite.GroupSingle()
        group_thing.add(name_text)
        group_thing.draw(self.head)

        """
        3. Money text
        """
        money_text = FontSave.get_font(3.5).render(f"${self.player_data.money:,}", True, DEFAULT_TEXT_COLOR)
        money_text_rect = money_text.get_rect(center=((w + r) / 2, 0.75 * h))
        self.head.blit(money_text, money_text_rect)


        """
        4. Profile picture

        (currently just a random color)
        """
        pygame.draw.circle(self.head, rand_color(), (r, r), r + 1)

    def draw_sub(self):
        """
        Draw the sub frame.
        """
        _, _, w, h = self.sub_rect

        """
        1. Sub frame base
        """
        sub_base = pygame.Surface((w, h), pygame.SRCALPHA)
        sub_base_rect = pygame.Rect(0, 0, w, h)

        draw_rounded_rect(sub_base, sub_base_rect, color=DEFAULT_SUB_COLOR)
        sub_base.set_alpha(150)
        self.sub.blit(sub_base, sub_base_rect)

        """
        2. Sub text
        """
        sub_text = FontSave.get_font(3).render(random.choice(rules.basic.HandRanking.TYPE_STR).capitalize(),
                                               True, DEFAULT_TEXT_COLOR)
        sub_text_rect = sub_text.get_rect(center=(w / 2, h / 2))

        self.sub.blit(sub_text, sub_text_rect)

    def init_components(self):
        for i in range(6):
            self.redraw_component(i)
            self.component_group.add(self.components[i])

    def redraw_component(self, component: int):
        match component:
            case Component.SUB_BASE:
                pass

            case Component.SUB_TEXT:
                pass

            case Component.HEAD_BASE:
                pass

            case Component.NAME_TEXT:
                pass

            case Component.MONEY_TEXT:
                pass

            case Component.PROFILE_PIC:
                pass


    def draw(self):
        """
        Draw the elements of a player display.
        """
        self.draw_head()
        self.draw_sub()

        self.image.blit(self.head, self.head_rect)
        self.image.blit(self.sub, self.sub_rect)


    def update(self):
        pass
        # self.draw()
