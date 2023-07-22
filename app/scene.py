import pygame
import pygame.sprite

from app import widgets
from app.shared import *


class Scene:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = pygame.sprite.Group()

        self.thing = widgets.button.Button(percent_to_px(50, 50), percent_to_px(15, 7.5), text="Hi",
                                           command=lambda: print("Hello, World!"), b_thickness=5)
        self.all_sprites.add(self.thing)

    def update(self):
        self.display_surface.fill("#123456")
        self.all_sprites.update()
        self.all_sprites.draw(self.display_surface)
