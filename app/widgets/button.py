import pygame
import pygame.sprite
import pygame.gfxdraw

from app.shared import *


class Button(pygame.sprite.Sprite):
    DEFAULT_COLOR = (43, 193, 193)
    DEFAULT_B_COLOR = (28, 144, 175)

    def __init__(self, pos, dimensions, color=DEFAULT_COLOR, command=None,
                 text="", text_color=(0, 0, 0), font=None, b_color=DEFAULT_B_COLOR, b_thickness=0):

        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.command = command if command else lambda: None

        """
        Button states
        """
        self.hover = False
        self.mouse_down = False
        self.prev_mouse_down = False

        """
        Button appearance
        """
        self.color = color
        self.b_color = b_color
        self.b_thickness = b_thickness

        """
        Button text
        """
        self.font = font if font else pygame.font.Font(DEFAULT_FONT_PATH, int(h_percent_to_px(4)))
        self.text = self.font.render(text, True, text_color)
        self.text_rect = self.text.get_rect(center=(self.rect.width / 2, self.rect.height / 2))

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        """
        Update button states
        """
        self.hover = self.rect.collidepoint(mouse_x, mouse_y)
        self.mouse_down = pygame.mouse.get_pressed()[0]  # Left mouse button

        """
        Detect button press
        
        Mouse is no longer pressed and the cursor is still on the button.
        """
        if not self.mouse_down and self.mouse_down != self.prev_mouse_down and self.hover:
            # Button press
            self.command()

        self.prev_mouse_down = self.mouse_down

        """
        Update button apperance
        """
        if self.hover:
            if self.mouse_down:
                self.draw_button(0.75)
            else:
                self.draw_button(1.25)

        else:
            self.draw_button(1)

        self.image.blit(self.text, self.text_rect)

    def draw_button(self, brightness=1.0):
        """
        Draw a rounded rectangle for the button with the set color and border color attributes.

        :param brightness: The brightness multiplier for the color and border color.
        """
        draw_rounded_rect(self.image, self.image.get_rect(topleft=(0, 0)),
                          hsv_factor(self.color, vf=brightness),
                          hsv_factor(self.b_color, vf=brightness), self.b_thickness)
