import pygame
import screen
from button import Button
from qol import draw_text

class Hud:
    def __init__(self):
        self.size_x = 320
        self.size_y = screen.WIN.get_height()
        self.icon_size = 40

        self.pos = screen.WIN.get_width() - self.size_x, 0

        self.font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 24)
        self.text_colour = (220, 220, 220)

        self.image_background = None
        self.image_icon_time = None
        self.image_icon_money = None
        self.image_icon_roads = None
        self.image_icon_trucks = None

        self.load_images()

        self.buttons = [Button(self.pos[0] + self.size_x * 2 / 7, self.pos[1] + 8 * self.icon_size, False), Button(self.pos[0] + self.size_x * 5 / 7, self.pos[1] + 8 * self.icon_size, False),
                        Button(self.pos[0] + self.size_x * 2 / 7 , self.pos[1] + 13 * self.icon_size, False), Button(self.pos[0] + self.size_x * 5 / 7, self.pos[1] + 13 * self.icon_size, False), ]
        self.buttons_text = [["Buy", "Road"], ["Buy", "Truck"], ["Buy", "Time"], ["Buy", "Land"]]

    def load_images(self):
        path = "assets/hud/"
        self.image_background = pygame.transform.scale(pygame.image.load(path+"background.png"), (self.size_x, self.size_y))
        self.image_icon_time = pygame.transform.scale(pygame.image.load(path+"icons/time.png"), (self.icon_size, self.icon_size))
        self.image_icon_money = pygame.transform.scale(pygame.image.load(path+"icons/money.png"), (self.icon_size, self.icon_size))
        self.image_icon_roads = pygame.transform.scale(pygame.image.load(path+"icons/roads.png"), (self.icon_size, self.icon_size))
        self.image_icon_trucks = pygame.transform.scale(pygame.image.load(path+"icons/trucks.png"), (self.icon_size, self.icon_size))

    def check_buttons(self, click: bool):
        for button in self.buttons:
            button.check_pressed(click)

    def draw(self, time: str = "00:00:00", money: str = "0", roads: str = "0", trucks: str = "0"):
        screen.WIN.blit(self.image_background, (screen.WIN.get_width() - self.size_x, 0))

        screen.WIN.blit(self.image_icon_time, (self.pos[0] + self.icon_size, self.pos[1] + self.icon_size))
        screen.WIN.blit(self.image_icon_money, (self.pos[0] + self.icon_size, self.pos[1] + 2.5 * self.icon_size))
        screen.WIN.blit(self.image_icon_roads, (self.pos[0] + self.icon_size, self.pos[1] + 4 * self.icon_size))
        screen.WIN.blit(self.image_icon_trucks, (self.pos[0] + self.size_x // 2+ self.icon_size * 0.5, self.pos[1] + 4 * self.icon_size))

        draw_text(screen.WIN, self.font, f"{time}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{money}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + 2.5 * self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{roads}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + 4 * self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{trucks}", (self.pos[0] + self.size_x // 2 + self.icon_size * 2, self.pos[1] + 4 * self.icon_size + 6), self.text_colour)

        for button, text in zip(self.buttons, self.buttons_text):
            button.draw(text)
