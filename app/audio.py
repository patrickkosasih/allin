import pygame
import os


sound_cache: dict[str, pygame.mixer.Sound] = {}


def play_sound(filename):
    sound = sound_cache.setdefault(filename, pygame.mixer.Sound(filename))
    sound.play()
