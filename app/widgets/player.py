import random

import pygame

import rules.game_flow
import rules.basic
from app.shared import *
from testing import func_timer


DEFAULT_COLOR = 95, 201, 123
DEFAULT_SUB_COLOR = 32, 46, 38
DEFAULT_TEXT_COLOR = 255, 255, 255


class Player(pygame.sprite.Sprite):
    """
    The `Player` class is the GUI representation of a player.
    """

    def __init__(self, pos, dimensions, player_data: rules.game_flow.PlayerData):
        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.player_data = player_data

        self.font = pygame.font.Font(DEFAULT_FONT_PATH, int(h_percent_to_px(3)))

        self.draw()

    def draw(self):
        """
        Draw the elements of a player display.
        """

        w, h = self.rect.width, self.rect.height
        h_main, h_sub = 0.7 * h, 0.3 * h
        r = h_main / 2

        """
        1. Sub frame
        """
        sub_rect = pygame.Rect(0.1 * w, h_main, 0.8 * w, h_sub)
        sub = pygame.Surface((sub_rect.width, sub_rect.height), pygame.SRCALPHA)

        draw_rounded_rect(sub, pygame.Rect(0, 0, sub_rect.width, sub_rect.height), color=DEFAULT_SUB_COLOR)
        sub.set_alpha(150)
        self.image.blit(sub, sub_rect)

        """
        2. Sub text
        """
        sub_text = self.font.render(random.choice(rules.basic.HandRanking.TYPE_STR).capitalize(),
                                    True, DEFAULT_TEXT_COLOR)
        self.image.blit(sub_text, sub_text.get_rect(center=sub_rect.center))

        """
        3. Main frame
        """
        draw_rounded_rect(self.image, pygame.Rect(0, 0, w, h_main), color=DEFAULT_COLOR, b=0)

        """
        4. Player name text
        """
        name_text = self.font.render(self.player_data.name, True, DEFAULT_TEXT_COLOR)
        name_text_rect = name_text.get_rect(center=((w + r) / 2, 0.25 * h_main))
        self.image.blit(name_text, name_text_rect)

        """
        5. Money text
        """
        money_text = self.font.render(f"${self.player_data.money:,}", True, DEFAULT_TEXT_COLOR)
        money_text_rect = money_text.get_rect(center=((w + r) / 2, 0.75 * h_main))
        self.image.blit(money_text, money_text_rect)

        """
        6. Profile picture
        
        (currently just a random color)
        """
        pygame.draw.circle(self.image, rand_color(), (r, r), r + 1)
