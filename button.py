import pygame
from qol import draw_text
import screen

class Button:
    def __init__(self, x: int, y: int, activated: bool = True):
        self.size_x = 100
        self.size_y = 160

        self.font = self.font = pygame.font.Font("assets/PublicPixel-z84yD.ttf", 12)

        self.button_center_pos = (x, y + self.size_y * 0.3)
        self.button_radius = self.size_x * 0.8

        self.draw_pos = (x - self.size_x // 2, y - self.size_y // 2)

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

    def check_pressed(self, clicked: bool):
        if clicked:
            x, y = pygame.mouse.get_pos()
            dx2, dy2 = (x - self.button_center_pos[0]) ** 2, (y - self.button_center_pos[1]) ** 2
            if dx2 + dy2 <= self.button_radius ** 2:
                self.pressed = 1
        else:
            self.pressed = 0

        return bool(self.pressed)

    def set_activation(self, activated: bool):
        self.deactivated = not activated

    def draw(self):
        screen.WIN.blit(self.images[self.deactivated][self.pressed], self.draw_pos)


if __name__ == '__main__':
    screen.init()

    b = Button(500, 500)

    while 1:
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    b.check_pressed(True)

            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    b.check_pressed(False)

        pygame.event.clear()

        screen.WIN.fill((52, 52, 52))
        b.draw()

        pygame.display.flip()

