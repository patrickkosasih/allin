import pygame
import pygame.sprite

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
        self.font = font if font else pygame.font.Font(DEFAULT_FONT_NAME, 40)
        self.text = self.font.render(text, True, text_color)
        self.text_rect = self.text.get_rect(center=(self.rect.width / 2, self.rect.height / 2))

    def draw_button(self, color=(0, 0, 0), b_color=(0, 0, 0), b=0):
        """
        Procedurally draw a rounded rectangle for the button.

        :param color: The inner color of the button
        :param b_color: The border color
        :param b: The border thickness. If set to 0 then the border is not drawn.
        :return:
        """

        x, y, w, h = self.rect
        r = h / 2

        if b >= 0:
            # Outer rounded rectangle (for the border)
            pygame.draw.rect(self.image, b_color, (r, 0, (w - 2 * r), h))
            pygame.draw.circle(self.image, b_color, (r, r), r)
            pygame.draw.circle(self.image, b_color, (w - r, r), r)

        # Inner rounded rectangle
        pygame.draw.rect(self.image, color, (r, b, (w - 2 * r), h - 2 * b))
        pygame.draw.circle(self.image, color, (r, r), r - b)
        pygame.draw.circle(self.image, color, (w - r, r), r - b)


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
                self.draw_button(hsv_factor(self.color, vf=0.75), hsv_factor(self.b_color, vf=0.75), self.b_thickness)
            else:
                self.draw_button(hsv_factor(self.color, vf=1.25), hsv_factor(self.b_color, vf=1.25), self.b_thickness)

        else:
            self.draw_button(self.color, self.b_color, self.b_thickness)



        self.image.blit(self.text, self.text_rect)
