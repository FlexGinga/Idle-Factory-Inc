import pygame
import screen
from qol import draw_text, seconds_to_time

def end_menu(total_time, total_money):
    size_x, size_y = size = screen.WIN.get_size()
    bg = pygame.transform.scale(pygame.image.load("assets/menu/bg.png"), size).convert()
    info_box = pygame.transform.scale(pygame.image.load("assets/menu/info_screen.png").convert_alpha(), (size_x * 0.5, size_y * 0.75))

    font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", size_y // 40)
    text = ["Statistics:", "------------", "", f"Time survived - {seconds_to_time(total_time)}", f"Money earned - £{total_money}"]

    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                run = False

        pygame.event.clear()

        screen.WIN.blit(bg, (0, 0))
        screen.WIN.blit(info_box, (size_x * 0.25, size_y * 0.125))
        draw_text(screen.WIN, font, text, (size_x // 2, size_y // 2), center_x=True, center_y=True)

        pygame.display.flip()
