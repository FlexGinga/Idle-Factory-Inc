import pygame
import pyautogui
import sys


def init(title: str = None, icon_path: str = None):
    pygame.init()

    global WIN
    WIN = pygame.display.set_mode(pyautogui.size(), pygame.FULLSCREEN | pygame.SRCALPHA)

    if title is not None:
        pygame.display.set_caption(title)
    if icon_path is not None:
        pygame.display.set_icon(pygame.image.load(icon_path))


def quit():
    pygame.quit()
    sys.exit()
    quit()
