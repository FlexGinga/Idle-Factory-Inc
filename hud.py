import pygame
import screen
from button import Button
from qol import draw_text

class Hud:
    def __init__(self):
        self.size_x = screen.WIN.get_height() / 27 * 8
        self.size_y = screen.WIN.get_height()
        self.icon_size = self.size_x / 8

        self.pos = screen.WIN.get_width() - self.size_x, 0

        self.font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 24)
        self.text_colour = (220, 220, 220)

        self.image_background = None
        self.image_upgrade_backing = None
        self.image_icon_time = None
        self.image_icon_money = None
        self.image_icon_roads = None
        self.image_icon_trucks = None

        self.image_red_haze = None

        self.load_images()

        self.buttons = [Button(self.pos[0] + self.size_x * 2 / 7, self.pos[1] + 7.5 * self.icon_size, False), Button(self.pos[0] + self.size_x * 5 / 7, self.pos[1] + 7.5 * self.icon_size, False),
                        Button(self.pos[0] + self.size_x * 2 / 7 , self.pos[1] + 11.5 * self.icon_size, False), Button(self.pos[0] + self.size_x * 5 / 7, self.pos[1] + 11.5 * self.icon_size, False), ]
        self.buttons_text = ["Road", "Truck", "Time", "Land"]

        self.controls = ["Controls:",
                         "MMB - Move",
                         "B - Build Mode"]

        self.message = None

    def load_images(self):
        path = "assets/hud/"
        self.image_background = pygame.transform.scale(pygame.image.load(path+"background.png").convert_alpha(), (self.size_x, self.size_y))
        self.image_upgrade_backing = pygame.transform.scale(pygame.image.load(path+"upgrade_background.png").convert_alpha(), (self.size_x, self.size_y))
        self.image_icon_time = pygame.transform.scale(pygame.image.load(path+"icons/time.png").convert_alpha(), (self.icon_size, self.icon_size))
        self.image_icon_money = pygame.transform.scale(pygame.image.load(path+"icons/money.png").convert_alpha(), (self.icon_size, self.icon_size))
        self.image_icon_roads = pygame.transform.scale(pygame.image.load(path+"icons/roads.png").convert_alpha(), (self.icon_size, self.icon_size))
        self.image_icon_trucks = pygame.transform.scale(pygame.image.load(path+"icons/trucks.png").convert_alpha(), (self.icon_size, self.icon_size))

        self.image_red_haze = pygame.transform.scale(pygame.image.load(path+"red_haze.png").convert_alpha(), screen.WIN.get_size())

    def update(self, dt):
        if self.message is not None:
            self.message[1] += dt
            if self.message[1] >= self.message[2]:
                self.message = None

    def update_buttons(self, click: bool) -> list:
        statuses = []
        for button in self.buttons:
            button.check_pressed(click)
            statuses.append(button.pressed)
        return statuses

    def get_button_statuses(self) -> list:
        statuses = []
        for button in self.buttons:
            statuses.append(button.pressed)
        return statuses

    def add_message(self, message: str, len_: float = 5):
        self.message = [message, 0, len_]

    def draw(self, time: str = "00:00:00", money: str = "0", roads: str = "0", trucks: str = "0",
             prices: list = ["", "", "", ""], time_left: float = 10,  upgrades: list = []):

        screen.WIN.blit(self.image_upgrade_backing, (screen.WIN.get_width() - self.size_x, 0))
        for upgrade in upgrades:
            pass

        screen.WIN.blit(self.image_background, (screen.WIN.get_width() - self.size_x, 0))

        screen.WIN.blit(self.image_icon_time, (self.pos[0] + self.icon_size, self.pos[1] + self.icon_size))
        screen.WIN.blit(self.image_icon_money, (self.pos[0] + self.icon_size, self.pos[1] + 2.5 * self.icon_size))
        screen.WIN.blit(self.image_icon_roads, (self.pos[0] + self.icon_size, self.pos[1] + 4 * self.icon_size))
        screen.WIN.blit(self.image_icon_trucks, (self.pos[0] + self.size_x // 2+ self.icon_size * 0.5, self.pos[1] + 4 * self.icon_size))

        draw_text(screen.WIN, self.font, f"{time}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{money}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + 2.5 * self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{roads}", (self.pos[0] + self.icon_size * 2.5, self.pos[1] + 4 * self.icon_size + 6), self.text_colour)
        draw_text(screen.WIN, self.font, f"{trucks}", (self.pos[0] + self.size_x // 2 + self.icon_size * 2, self.pos[1] + 4 * self.icon_size + 6), self.text_colour)

        for button, text, price in zip(self.buttons, self.buttons_text, prices):
            button.draw(text, price)

        draw_text(screen.WIN, self.font, self.controls, (self.pos[0] + self.size_x / 2, self.pos[1] + self.size_y * 0.9), self.text_colour, center_x=True, center_y=True)

        if self.message is not None:
            draw_text(screen.WIN, self.font, [self.message[0]], (screen.WIN.get_width() // 2, screen.WIN.get_height() - 100), (255, 75, 60), center_x=True, center_y=True)

        if time_left < 10 and (0.3 > time_left % 1 or 0.7 < time_left % 1):
            screen.WIN.blit(self.image_red_haze, (0, 0))