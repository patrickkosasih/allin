import pygame
import pygame.sprite
import pygame.gfxdraw

from app.animations.anim_group import AnimGroup
from app.shared import *


class Button(pygame.sprite.Sprite):
    DEFAULT_COLOR = (43, 193, 193)

    def __init__(self, pos, dimensions, color=DEFAULT_COLOR, command=None,
                 text_str="", text_color=(255, 255, 255), font=None, b_color=None, b_thickness=0,
                 icon: pygame.Surface or None = None, icon_size: float = 1.0):

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
        self.b_color = b_color if b_color else hsv_factor(color, vf=0.75)
        self.b_thickness = b_thickness
        self.text_color = text_color

        """
        Components
        """
        self.component_group = pygame.sprite.Group()

        # Base
        self.base = pygame.sprite.Sprite(self.component_group)
        self.base.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.base.rect = self.base.image.get_rect(topleft=(0, 0))

        self.draw_base()

        # Text
        self.text = pygame.sprite.Sprite(self.component_group)
        self.font = font if font else FontSave.get_font(4)
        self.text_str = text_str

        self.set_text(self.text_str)

        # Icon
        self.icon = pygame.sprite.Sprite(self.component_group)
        self.set_icon(icon, icon_size)

        # Anim group
        self.anim_group = AnimGroup()

    def draw_base(self):
        """
        Draw a rounded rectangle for the button with the set color and border color attributes.
        """
        draw_rounded_rect(self.base.image, self.base.rect, self.color, self.b_color, self.b_thickness)

    def set_text(self, text_str: str):
        self.text_str = text_str

        self.text.image = self.font.render(self.text_str, True, self.text_color)
        self.text.rect = self.text.image.get_rect(center=(self.rect.width / 2, self.rect.height / 2))

    def set_icon(self, icon: pygame.Surface, size=1.0):
        if not icon:
            icon = pygame.Surface((1, 1), pygame.SRCALPHA)

        self.icon.image = pygame.transform.smoothscale(icon, 2 * (size * self.rect.height,))
        self.icon.rect = self.icon.image.get_rect(center=2 * (self.rect.height / 2,))

    def brighten(self, brightness):
        """
        Fill the image with the BLEND_ADD or BLEND_SUB special flag to brighten/darken the button.

        :param brightness: The brightness factor. If the value is negative then the button is darkened. Value must be
        between -255 to 255.
        """
        if brightness >= 0:
            self.image.fill(3 * (brightness,), special_flags=pygame.BLEND_ADD)

        else:
            self.image.fill(3 * (-brightness,), special_flags=pygame.BLEND_SUB)

    def update(self, dt):
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
        self.anim_group.update(dt)

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)

        if self.hover:
            if self.mouse_down:
                self.brighten(-30)
            else:
                self.brighten(30)

