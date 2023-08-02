import pygame
import pygame.sprite

from app import widgets
from app.shared import *


class Scene:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = pygame.sprite.LayeredUpdates()

    def update(self, dt):
        self.display_surface.fill("#123456")
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)
