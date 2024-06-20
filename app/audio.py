import pygame

from app import app_settings


"""
Sound Effects
"""
class SoundGroup:
    sound_cache: dict[str, pygame.mixer.Sound] = {}
    volume = 1.0

    @staticmethod
    def play_sound(filename, volume_mult=1.0):
        sound = SoundGroup.sound_cache.setdefault(filename, pygame.mixer.Sound(filename))
        sound.set_volume(SoundGroup.volume * volume_mult)
        sound.play()

    @staticmethod
    def update_volume():
        SoundGroup.volume = app_settings.main.get_value("sfx_volume")

    @staticmethod
    def stop_all_sounds():
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).fadeout(1000)


def play_sound(filename, volume_mult=1.0):
    SoundGroup.play_sound(filename, volume_mult)


"""
Music
"""
class MusicPlayer:
    playing = False

    @staticmethod
    def play(intro=False):
        if app_settings.main.get_value("music_volume") <= 0:
            return

        MusicPlayer.playing = True

        if intro:
            pygame.mixer.music.load("assets/audio/music/intro.ogg")
        else:
            pygame.mixer.music.load("assets/audio/music/short intro.ogg")

        pygame.mixer.music.play(fade_ms=250)
        pygame.mixer.music.queue("assets/audio/music/loop.ogg", loops=-1)

    @staticmethod
    def stop(fade_ms=2500):
        MusicPlayer.playing = False
        pygame.mixer.music.fadeout(fade_ms)

    @staticmethod
    def update_volume(autoplay=True):
        volume = app_settings.main.get_value("music_volume")

        if not MusicPlayer.playing and volume > 0 and autoplay:
            MusicPlayer.play()

        pygame.mixer.music.set_volume(volume)
