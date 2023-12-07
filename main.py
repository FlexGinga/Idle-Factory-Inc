from hub_spawns import HUB_SPAWNS
from os import listdir
from tile import Tile
import pygame

class Map:
    def __init__(self):
        self.grid_size_x = 0
        self.grid_size_y = 0
        self.tile_grid = []

        self.images = []
        self.image_hover = None

        self.scaled_images = []
        self.scaled_image_hover = None

        self.load_images()

        self.scale = 4

        self.tile_size = 16
        self.scaled_tile_size = int(self.scale * self.tile_size)
        self.scaled_tile_size_half = self.scaled_tile_size // 2

        self.scale_images()

        self.offset_constant_x = 0
        self.offset_constant_y = 0

        self.offset_x = 0
        self.offset_y = 0

        self.hover_tile_pos = None

        self.stage = 0

        self.create_grid()

    def load_images(self):
        paths = ["assets/map/decorations/", "assets/map/road/", "assets/map/tiles/"]
        for path in paths:
            image_set = []
            scaled_image_set = []
            for image in listdir(path):
                rotations = []
                scaled_rotations = []
                for i in range(4):
                    rotations.append(pygame.transform.rotate(pygame.image.load(path + image).convert(), 90 * i))
                    scaled_rotations.append(None)
                image_set.append(rotations)
                scaled_image_set.append(scaled_rotations)
            self.images.append(image_set)
            self.scaled_images.append(scaled_image_set)

        self.image_hover = pygame.image.load("assets/hover.png").convert_alpha()

    def scale_images(self):
        size = (self.scaled_tile_size, self.scaled_tile_size)
        for i, image_set in enumerate(self.images):
            for j, rotation_set in enumerate(image_set):
                for k, image in enumerate(rotation_set):
                    self.scaled_images[i][j][k] = pygame.transform.scale(image, size)

        self.scaled_image_hover = pygame.transform.scale(self.image_hover, size)

    def change_scale(self, delta):
        mouse_before = self.screen_to_grid(pygame.mouse.get_pos())

        self.scale += delta * self.scale / 10
        self.scale = clamp(self.scale, 2, 10)
        self.scaled_tile_size = int(self.scale * self.tile_size)
        self.scaled_tile_size_half = self.scaled_tile_size // 2
        self.scale_images()

        mouse_after = self.screen_to_grid(pygame.mouse.get_pos())

        self.offset_x -= (mouse_before[0] - mouse_after[0]) * self.scaled_tile_size
        self.offset_y -= (mouse_before[1] - mouse_after[1]) * self.scaled_tile_size

    def change_offset(self, delta_x, delta_y):
        self.offset_x += delta_x
        self.offset_y += delta_y

    def screen_to_grid(self, screen_pos):
        x, y = screen_pos
        x = (x - WIN.get_width() // 2 - self.offset_x + self.offset_constant_x) / self.scaled_tile_size
        y = (y - WIN.get_height() // 2 - self.offset_y + self.offset_constant_y) / self.scaled_tile_size
        return x, y

    def grid_to_screen(self, grid_pos):
        x, y = grid_pos
        x = x * self.scaled_tile_size - self.offset_constant_x + self.offset_x + WIN.get_width() // 2
        y = y * self.scaled_tile_size - self.offset_constant_y + self.offset_y + WIN.get_height() // 2
        return x, y

    @staticmethod
    def get_stage_size(stage):
        return 7 + stage * 4, 5 + stage * 2

    def build_hub(self):
        x_dif = (self.grid_size_x - len(HUB_SPAWNS[self.stage][0])) // 2
        y_dif = (self.grid_size_y - len(HUB_SPAWNS[self.stage])) // 2

        for y, row in enumerate(self.tile_grid[y_dif: self.grid_size_y - y_dif]):
            for x, tile in enumerate(row[x_dif: self.grid_size_x - x_dif]):
                self.tile_grid[y + y_dif][x + x_dif] = HUB_SPAWNS[self.stage][y][x]

    def create_grid(self, stage: int = 0):
        self.stage = stage
        self.grid_size_x, self.grid_size_y = self.get_stage_size(stage)

        self.tile_grid = [[Tile(tile_set=0, tile_type=0, tile_rotation=0) for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        self.build_hub()

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def expand_grid(self):
        self.stage += 1
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        old = self.tile_grid
        self.tile_grid = [[Tile(tile_set=0, tile_type=0, tile_rotation=0) for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        for y, row in enumerate(old):
            for x, tile in enumerate(row):
                self.tile_grid[y + 1][x + 2] = tile
        self.build_hub()

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def decide_tile_type(self, tile_pos, center: bool = False):
        neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        neighbouring_tiles_pos = []
        neighbours_road = []
        num_connections = 0

        for dx, dy in neighbours:
            neighbouring_tiles_pos.append([tile_pos[0] + dx, tile_pos[1] + dy])
            if 0 <= neighbouring_tiles_pos[-1][1] < self.grid_size_y and 0 <= neighbouring_tiles_pos[-1][0] < self.grid_size_x and self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_set == 1 and (self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].connectable or self.tile_grid[tile_pos[1]][tile_pos[0]].unbreakable):
                neighbours_road.append(1)
                num_connections += 1
            else:
                neighbouring_tiles_pos.pop(-1)
                neighbours_road.append(0)

        if self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set == 1:
            match num_connections:
                case 0:
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 0
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = 0
                case 1:
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 1
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = 3 - neighbours_road.index(1)
                case 2:
                    if neighbours_road in [[0, 1, 0, 1], [1, 0, 1, 0]]:
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 2
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = [[0, 1, 0, 1], [1, 0, 1, 0]].index(neighbours_road)
                    else:
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 3
                        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = [[0, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 0], [1, 0, 0, 1]].index(neighbours_road)
                case 3:
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 4
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = [[0, 1, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1]].index(neighbours_road)
                case 4:
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_set = 1
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type = 7
                    self.tile_grid[tile_pos[1]][tile_pos[0]].tile_rotation = 0

        if center:
            for pos in neighbouring_tiles_pos:
                if self.tile_grid[pos[1]][pos[0]].tile_set == 1 and self.tile_grid[pos[1]][pos[0]].connectable:
                    self.decide_tile_type(pos)

    def on_click(self, del_: bool = False):
        if self.hover_tile_pos is not None:
            tile = self.tile_grid[self.hover_tile_pos[1]][self.hover_tile_pos[0]]
            if not tile.unbreakable:
                if del_ and tile.tile_set == 1:
                    tile.tile_set = 0
                    tile.tile_type = 0
                    tile.tile_rotation = 0
                    self.decide_tile_type(self.hover_tile_pos, True)
                elif not del_:
                    tile.tile_set = 1
                    self.decide_tile_type(self.hover_tile_pos, True)

    def update(self):
        tile_x, tile_y = self.screen_to_grid(pygame.mouse.get_pos())
        tile_x, tile_y = int(tile_x), int(tile_y)
        if 0 <= tile_x < self.grid_size_x and 0 <= tile_y < self.grid_size_y:
            self.hover_tile_pos = tile_x, tile_y
        else:
            self.hover_tile_pos = None

    def draw(self):
        top_left_tile_pos = self.screen_to_grid((0, 0))
        bottom_right_tile_pos = self.screen_to_grid((WIN.get_width(), WIN.get_height()))

        for y, row in enumerate(self.tile_grid):
            for x, tile in enumerate(row):
                screen_x, screen_y = self.grid_to_screen((x, y))
                if -self.scaled_tile_size <= screen_x < WIN.get_width() and -self.scaled_tile_size <= screen_y < WIN.get_height():
                    WIN.blit(self.scaled_images[tile.tile_set][tile.tile_type][tile.tile_rotation], (screen_x, screen_y))

        if self.hover_tile_pos is not None:
            x, y = self.grid_to_screen(self.hover_tile_pos)
            WIN.blit(self.scaled_image_hover, (x, y))


if __name__ == '__main__':
    import pyautogui
    from time import time
    from qol import *

    pygame.init()
    WIN = pygame.display.set_mode(pyautogui.size(), pygame.FULLSCREEN | pygame.SRCALPHA)

    map = Map()

    FONT = pygame.font.SysFont('Comic Sans MS', 30)

    dragging = 0
    clicked = 0
    clicked_type = 0
    run = 1
    prev = time() - 0.001
    while run:
        now = time()
        dt = now - prev
        prev = now

        for e in pygame.event.get():
            if e.type == pygame.MOUSEWHEEL:
                map.change_scale(e.y)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    clicked = 1
                    if clicked_type == 0:
                        clicked_type = 1

                if e.button == 2:
                    dragging = 1
                    prev_pos = pygame.mouse.get_pos()

                if e.button == 3:
                    clicked = 1
                    if clicked_type == 0:
                        clicked_type = 2

            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    clicked = 0
                    clicked_type = 0

                if e.button == 2:
                    dragging = 0

                if e.button == 3:
                    clicked = 0
                    clicked_type = 0

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = 0

                if e.key == pygame.K_r:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_rotation += 1
                        tile.tile_rotation %= 4

                if e.key == pygame.K_t:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_type += 1
                        tile.tile_rotation = 0
                        tile.tile_type %= len(map.images[tile.tile_set])

                if e.key == pygame.K_y:
                    if map.hover_tile_pos is not None:
                        tile = map.tile_grid[map.hover_tile_pos[1]][map.hover_tile_pos[0]]
                        tile.tile_set += 1
                        tile.tile_type = 0
                        tile.tile_rotation = 0
                        tile.tile_set %= len(map.images)

                if e.key == pygame.K_SPACE:
                    print(map.tile_grid)
                    map.expand_grid()

        if dragging:
            current_pos = pygame.mouse.get_pos()
            map.change_offset(current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
            prev_pos = current_pos

        if clicked:
            map.on_click(bool(clicked_type-1))

        pygame.event.clear()

        map.update()

        WIN.fill((52, 52, 52))
        map.draw()

        # draw_text(WIN, FONT, f"FPS:: {int(1 / dt)}", 10, 40)

        pygame.display.flip()

    pygame.quit()
