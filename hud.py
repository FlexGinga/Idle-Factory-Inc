import pygame
import screen
from button import Button
from qol import draw_text

class Hud:
    def __init__(self):
        self.size_x = 320
        self.size_y = screen.WIN.get_height()
        self.icon_size = 40

        self.font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 24)
        self.text_colour = (220, 220, 220)

        self.image_background = None
        self.image_icon_time = None
        self.image_icon_money = None
        self.image_icon_road = None

        self.load_images()

        self.buttons = [Button(0, 0, False)]

    def load_images(self):
        path = "assets/hud/"
        self.image_background = pygame.transform.scale(pygame.image.load(path+"background.png"), (self.size_x, self.size_y))
        self.image_icon_time = pygame.transform.scale(pygame.image.load(path+"icons/time.png"), (self.icon_size, self.icon_size))
        self.image_icon_money = pygame.transform.scale(pygame.image.load(path+"icons/money.png"), (self.icon_size, self.icon_size))
        self.image_icon_road = pygame.transform.scale(pygame.image.load(path+"icons/roads.png"), (self.icon_size, self.icon_size))

    def draw(self, time: str = "00:00:00", money: str = "0", roads: str = "0"):
        screen.WIN.blit(self.image_background, (screen.WIN.get_width() - self.size_x, 0))

        screen.WIN.blit(self.image_icon_time, (screen.WIN.get_width() - self.size_x + self.icon_size, self.icon_size))
        screen.WIN.blit(self.image_icon_money, (screen.WIN.get_width() - self.size_x + self.icon_size, 2.5 * self.icon_size))
        screen.WIN.blit(self.image_icon_road, (screen.WIN.get_width() - self.size_x + self.icon_size, 4 * self.icon_size))

        draw_text(screen.WIN, self.font, f"{time}", (screen.WIN.get_width() - self.size_x + self.icon_size * 2.5, self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{money}", (screen.WIN.get_width() - self.size_x + self.icon_size * 2.5, 2.5 * self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{roads}", (screen.WIN.get_width() - self.size_x + self.icon_size * 2.5, 4 * self.icon_size + 6), self.text_colour)
