import pygame

current_music = ""


def play(name, volume):
    global current_music
    if current_music == name:
        return
    pygame.mixer.music.load("res/music/" + name)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=-1, fade_ms=1000)
    current_music = name

