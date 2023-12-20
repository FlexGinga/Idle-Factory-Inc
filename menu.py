import pygame
import screen
from time import time

def menu():
    size_x, size_y = size = screen.WIN.get_size()
    bg = pygame.transform.scale(pygame.image.load("assets/menu/bg.png"), size)
    logo = pygame.transform.scale(pygame.image.load("assets/menu/name.png"), (size_x // 2, size_y // 4))
    text = pygame.transform.scale(pygame.image.load("assets/menu/text.png"), (size_x * 2, size_y // 48))

    text_speed = 10
    c = 0

    prev = time() - 0.001
    playing = False
    while not playing:
        now = time()
        dt = now - prev
        prev = now

        c += dt
        if c >= text_speed:
            c -= text_speed

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return True
                if e.key == pygame.K_SPACE:
                    playing = True
        pygame.event.clear()

        screen.WIN.blit(bg, (0, 0))
        screen.WIN.blit(logo, (size_x // 4, size_y // 8))
        screen.WIN.blit(text, (c / text_speed * -size_x, size_y - size_y // 48))
        pygame.display.flip()
