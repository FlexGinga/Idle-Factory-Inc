import pygame
from qol import draw_text
import screen

class Button:
    def __init__(self, x: int, y: int, activated: bool = True):
        """

        :param x:
        :param y:
        :param activated:

        pos of x and y is center of button object
        """

        self.size_x = 100
        self.size_y = 160

        self.font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 12)

        self.button_center_pos = (x, y + self.size_y * 0.2)
        self.button_radius = self.size_x * 0.4

        self.draw_pos = x - self.size_x // 2, y - self.size_y // 2
        self.text_pos = x, y - self.size_y * 0.3

        path = "assets/hud/buttons/"
        self.image_activated = pygame.transform.scale(pygame.image.load(path+"activated.png"), (self.size_x, self.size_y))
        self.image_activated_pressed = pygame.transform.scale(pygame.image.load(path+"activated_pressed.png"), (self.size_x, self.size_y))
        self.image_deactivated = pygame.transform.scale(pygame.image.load(path+"deactivated.png"), (self.size_x, self.size_y))
        self.image_deactivated_pressed = pygame.transform.scale(pygame.image.load(path+"deactivated_pressed.png"), (self.size_x, self.size_y))

        self.images = [
            [self.image_activated, self.image_activated_pressed],
            [self.image_deactivated, self.image_deactivated_pressed]
        ]

        self.deactivated = int(not activated)
        self.pressed = 0

    def check_pressed(self, click: bool):
        if click:
            x, y = pygame.mouse.get_pos()
            dx2, dy2 = (x - self.button_center_pos[0]) ** 2, (y - self.button_center_pos[1]) ** 2
            if dx2 + dy2 <= self.button_radius ** 2:
                self.pressed = 1
        else:
            self.pressed = 0

        return bool(self.pressed)

    def set_activation(self, activated: bool):
        self.deactivated = not activated

    def draw(self, text, price):
        screen.WIN.blit(self.images[self.deactivated][self.pressed], self.draw_pos)
        draw_text(screen.WIN, self.font, [text, str(price)], self.text_pos, colour=(23, 23, 23), center_x=True, center_y=True)
