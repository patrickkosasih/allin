import pygame
import pygame.sprite
import pygame.gfxdraw

from app.animations.anim_group import AnimGroup
from app.shared import *


class Button(pygame.sprite.Sprite):
    DEFAULT_COLOR = (43, 193, 193)

    def __init__(self, pos, dimensions, color=DEFAULT_COLOR, command: Callable = None,
                 text_str="", text_color=(255, 255, 255), font: pygame.font.Font = None,
                 b_color=None, b_thickness=0, rrr=0,
                 icon: pygame.Surface or None = None, icon_size: float = 1.0,
                 text_align="middle", icon_align="left", text_align_offset=0):

        """
        Parameters:

        :param pos: Center position of button.
        :param dimensions: Dimensions of button.
        :param color: Background color of button.
        :param command: The function that is run when the button is clicked.

        :param text_str: The string data of the button's text.
        :param text_color: Text / foreground color of button.
        :param font: The font of the button's text.

        :param b_color: The color of the button's border.
        :param b_thickness: The thickness of the button's border. If set to 0 then no border is drawn.
        :param rrr: The corner radius of the rounded rectangle-shaped button. RRR: Rounded rectangle radius.

        :param icon: The icon of the button
        :param icon_size: The scale of the icon based on the button's height. Icon height = Button height * Icon size.

        :param text_align: The alignment of the text. Possible alignments: "middle" (default), "top", "bottom".
        :param icon_align: The alignment of the icon. Possible alignments: "left" (default), "right", "middle".
        :param text_align_offset: The offset of the text when it is aligned at the top or bottom.
                                  Text y pos = Original text y pos +- (Button height * Text align offset).
        """

        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.global_rect = self.rect.copy()

        """
        General button attributes
        """
        self.command = command if command else lambda: None
        self.disabled = False

        """
        Mouse states
        """
        self.hover = False
        self.mouse_down = False
        self.prev_mouse_down = False
        self.selected = False

        """
        Button appearance
        """
        self.color = color
        self.b_color = b_color if b_color else hsv_factor(color, vf=0.75)
        self.b_thickness = b_thickness
        self.text_color = text_color
        self.rrr = rrr

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
        self.text_align = text_align
        self.text_align_offset = text_align_offset

        self.set_text(self.text_str)

        # Icon
        self.icon = pygame.sprite.Sprite(self.component_group)
        self.icon_size = icon_size
        self.icon_align = icon_align

        self.set_icon(icon, icon_size)

        # Anim group
        self.anim_group = AnimGroup()

    def draw_base(self):
        """
        Draw a rounded rectangle for the button with the set color and border color attributes.
        """
        draw_rounded_rect(self.base.image, self.base.rect, self.color, self.b_color, self.b_thickness, self.rrr)

    def set_text(self, text_str: str):
        self.text_str = text_str
        self.text.image = self.font.render(self.text_str, True, self.text_color)

        x = self.rect.w / 2

        match self.text_align:
            case "top":     y = self.text.image.get_height() / 2 + self.rect.h * self.text_align_offset
            case "middle":  y = self.rect.h / 2
            case "bottom":  y = self.rect.h - self.text.image.get_height() / 2 - self.rect.h * self.text_align_offset
            case _:         raise ValueError(f"invalid text alignment: {self.text_align}")

        self.text.rect = self.text.image.get_rect(center=(x, y))

    def set_icon(self, icon: pygame.Surface, size=1.0):
        if not icon:
            icon = pygame.Surface((1, 1), pygame.SRCALPHA)
            self.icon.image = icon
            self.icon.rect = (0, 0, 1, 1)
            return

        """
        Icon positioning
        
        Icon height = Button height * Icon size.
        Icon width = (Original width / Original height) * New icon height.
        """

        h = int(self.rect.h * size)
        w = int((icon.get_width() / icon.get_height()) * h)

        y = self.rect.h / 2

        match self.icon_align:
            case "left":    x = y
            case "middle":  x = self.rect.w / 2
            case "right":   x = self.rect.w - y
            case _:         raise ValueError(f"invalid icon alignment: {self.icon_align}")

        """
        Set attributes
        """
        self.icon_size = size

        self.icon.image = pygame.transform.smoothscale(icon, (w, h))
        self.icon.rect = self.icon.image.get_rect(center=(x, y))

    def set_color(self, color=None, b_color=None):
        if color:
            self.color = color
        if b_color:
            self.b_color = b_color

        self.draw_base()

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
        self.hover = self.global_rect.collidepoint(mouse_x, mouse_y)
        self.mouse_down = pygame.mouse.get_pressed()[0]  # Left mouse button

        """
        Update button states and detect button press
        """
        if self.hover and not self.mouse_down and self.prev_mouse_down and self.selected:
            # Button press
            self.command()

        if self.hover and self.mouse_down and not self.prev_mouse_down:
            self.selected = True
        elif not self.mouse_down:
            self.selected = False

        self.prev_mouse_down = self.mouse_down

        """
        Update button apperance
        """
        self.anim_group.update(dt)

        self.image.fill((0, 0, 0, 0))
        self.component_group.draw(self.image)

        if self.hover and not self.disabled:
            if self.mouse_down:
                self.brighten(-30)
            else:
                self.brighten(30)
