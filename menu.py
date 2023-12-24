import pygame
import screen
from time import time
from qol import draw_text

def menu():
    size_x, size_y = size = screen.WIN.get_size()
    bg = pygame.transform.scale(pygame.image.load("assets/menu/bg.png"), size).convert()
    logo = pygame.transform.scale(pygame.image.load("assets/menu/name.png"), (size_x // 2, size_y // 4)).convert()
    text = pygame.transform.scale(pygame.image.load("assets/menu/text.png"), (size_x * 2, size_y // 48)).convert_alpha()

    seed_box = pygame.transform.scale(pygame.image.load("assets/menu/seed_box.png"), (size_x // 4, size_y // 16)).convert()
    seed_key = {48 : "0", 49 : "1", 50 : "2", 51 : "3", 52 : "4", 53 : "5", 54 : "6", 55 : "7", 56 : "8", 57 : "9",
                97 : "a", 98 : "b", 99 : "c", 100 : "d", 101 : "e", 102 : "f", 103 : "g", 104 : "h", 105 : "i",
                106 : "j", 107 : "k", 108 : "l", 109 : "m", 110 : "n", 111 : "o", 112 : "p", 113 : "q", 114 : "r",
                115 : "s", 116 : "t", 117 : "u", 118 : "v", 119 : "w", 120 : "x", 121 : "y", 122 : "z"}
    max_seed_length = 27
    font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 16)

    seed = ""

    text_speed = 10
    c = 0

    prev = time() - 0.001

    exit_ = False
    run = True
    while run:
        now = time()
        dt = now - prev
        prev = now

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = False
                    exit_ = True
                if e.key == pygame.K_SPACE:
                    run = False

                if e.key == pygame.K_BACKSPACE:
                    if len(seed) > 0:
                        seed = seed[:-1]
                if e.key in seed_key and len(seed) < max_seed_length:
                    seed += seed_key[e.key]

        pygame.event.clear()

        c += dt
        if c >= text_speed:
            c -= text_speed

        screen.WIN.blit(bg, (0, 0))
        screen.WIN.blit(logo, (size_x // 4, size_y // 8))

        screen.WIN.blit(seed_box, (size_x // 2 - size_x // 8, size_y // 2))
        draw_text(screen.WIN, font, ["seed:", seed], (size_x // 2, size_y // 2 + size_y // 32), center_x=True, center_y=True)

        screen.WIN.blit(text, (c / text_speed * -size_x, size_y - size_y // 48))
        pygame.display.flip()

    return seed, exit_
