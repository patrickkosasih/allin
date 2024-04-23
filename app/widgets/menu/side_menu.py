import pygame
from pygame import Vector2

from app.shared import Layer
from app.widgets.basic.button import CircularButton, Button
from app.widgets.basic.panel import Panel
from app.animations.interpolations import *

INGAME_MENU_COLOR = (10, 10, 10, 100)


class SideMenu(Panel):
    def __init__(self, parent, *rect_args, toggle_button: "SideMenuButton", **panel_kwargs):

        super().__init__(parent, *rect_args, base_color=INGAME_MENU_COLOR,
                         outer_margin=2, base_radius=0, pack_height=7.5, **panel_kwargs)
        self.layer = Layer.SIDE_MENU

        """
        Buttons
        """
        # Back button
        bx, by, bw, bh = self.next_pack_rect
        self.add_scrollable(CircularButton(self, bx, by, bh / 2,
                                           command=self.back_click,
                                           icon=pygame.image.load("assets/sprites/action icons/cancel.png"), icon_size=0.9))

        # Home/main menu button
        self.add_scrollable(Button(self, *self.next_pack_rect, text_str="Main Menu",
                                   command=self.main_menu_click,
                                   icon=pygame.image.load("assets/sprites/menu icons/home.png"), icon_size=0.95))

        # Quit button
        self.add_scrollable(Button(self, *self.next_pack_rect, text_str="Close Game",
                                   command=self.quit_click,
                                   icon=pygame.image.load("assets/sprites/menu icons/quit.png"), icon_size=0.9))


        """
        Toggle button
        """
        self.toggle_button = toggle_button
        self.toggle_button.menu = self

        """
        Hidden/unhidden attributes
        """
        self.original_pos = self.rect.topleft
        self.hidden_pos = Vector2(self.rect.topleft) - Vector2(self.rect.width, 0)

    def back_click(self):
        self.set_shown(False)
        self.toggle_button.set_shown(True)

    def main_menu_click(self):
        # FIXME The game still runs in the background after going to the main menu.
        self.scene.app.change_scene("mainmenu")

    def quit_click(self):
        self.scene.app.quit()

    def set_shown(self, shown: bool, duration=0.4):
        self.move_anim(duration, self.original_pos if shown else self.hidden_pos, "px", "tl", "tl",
                       interpolation=ease_out if shown else ease_in_out)

    def on_mouse_down(self, event):
        super().on_mouse_down(event)

        if not self.rect.global_rect.collidepoint(self.mouse_x, self.mouse_y):
            self.back_click()


class SideMenuButton(CircularButton):
    def __init__(self, parent, *rect_args):
        super().__init__(parent, *rect_args, command=self.command,
                         icon=pygame.image.load("assets/sprites/menu icons/side menu.png"), icon_size=0.75)

        self.menu = None

    def command(self):
        if not self.menu:
            return

        self.set_shown(False)
        self.menu.set_shown(True)

    def set_shown(self, shown: bool, duration=0.2):
        self.disabled = not shown
        self.fade_anim(duration, 255 if shown else 0)
