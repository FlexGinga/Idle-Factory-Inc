from hub_spawns import HUB_SPAWNS
from os import listdir
from tile import Tile
from car import Car
from perlin_noise import PerlinNoise2D
from effect import Effect
from pathfinding import AStar
import screen
from qol import clamp
import pygame


class Map:
    def __init__(self, prn):
        self.prn = prn

        self.grid_size_x = 0
        self.grid_size_y = 0
        self.tile_grid = []

        self.images = []
        self.image_hover = None
        self.images_effect = []

        self.scaled_images = []
        self.scaled_image_hover = None
        self.scaled_images_effect = []

        self.image_build_mode = None

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

        self.noise_scale = 10
        self.perlin_noise = PerlinNoise2D(prn.generate())

        self.factories = []
        self.create_grid()

        self.image_car = pygame.image.load("assets/cars/truck.png")
        self.scaled_car = pygame.transform.scale(self.image_car, (self.scaled_tile_size / 3, self.scaled_tile_size * 2 / 3))

        self.cars = []

        self.effects = []

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

        path = "assets/map/effect/"
        for image in listdir(path):
            self.images_effect.append(pygame.image.load(path + image).convert_alpha())
            self.scaled_images_effect.append(None)

        self.image_hover = pygame.image.load("assets/map/hover.png").convert_alpha()
        self.image_build_mode = pygame.transform.scale(pygame.image.load("assets/map/build_mode_icon.png").convert_alpha(), (48,32))

    def scale_images(self):
        size = (self.scaled_tile_size, self.scaled_tile_size)
        for i, image_set in enumerate(self.images):
            for j, rotation_set in enumerate(image_set):
                for k, image in enumerate(rotation_set):
                    self.scaled_images[i][j][k] = pygame.transform.scale(image, size)

        for i, image in enumerate(self.images_effect):
            self.scaled_images_effect[i] = pygame.transform.scale(image, size)

        self.scaled_image_hover = pygame.transform.scale(self.image_hover, size)

    def change_scale(self, delta):
        mouse_before = self.screen_to_grid(pygame.mouse.get_pos())

        self.scale += delta * self.scale / 10
        self.scale = clamp(self.scale, 0.25, 10)
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
        x = (x - screen.WIN.get_width() // 2 - self.offset_x + self.offset_constant_x) / self.scaled_tile_size
        y = (y - screen.WIN.get_height() // 2 - self.offset_y + self.offset_constant_y) / self.scaled_tile_size
        return x, y

    def grid_to_screen(self, grid_pos):
        x, y = grid_pos
        x = x * self.scaled_tile_size - self.offset_constant_x + self.offset_x + screen.WIN.get_width() // 2
        y = y * self.scaled_tile_size - self.offset_constant_y + self.offset_y + screen.WIN.get_height() // 2
        return x, y

    @staticmethod
    def get_stage_size(stage):
        return 9 + stage * 4, 7 + stage * 2

    def build_hub(self):
        x_dif = (self.grid_size_x - len(HUB_SPAWNS[self.stage][0])) // 2
        y_dif = (self.grid_size_y - len(HUB_SPAWNS[self.stage])) // 2

        for y, row in enumerate(self.tile_grid[y_dif: self.grid_size_y - y_dif]):
            for x, tile in enumerate(row[x_dif: self.grid_size_x - x_dif]):
                self.tile_grid[y + y_dif][x + x_dif] = HUB_SPAWNS[self.stage][y][x]

        for y, row in enumerate(self.tile_grid[y_dif: self.grid_size_y - y_dif]):
            for x, tile in enumerate(row[x_dif: self.grid_size_x - x_dif]):
                if tile.tile_set == 1:
                    neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                    neighbouring_tiles_pos = []

                    for dx, dy in neighbours:
                        neighbouring_tiles_pos.append([x + dx, y + dy])
                        if not (0 <= neighbouring_tiles_pos[-1][1] < self.grid_size_y and 0 <= neighbouring_tiles_pos[-1][0] < self.grid_size_x and self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_set == 1):
                            neighbouring_tiles_pos.pop(-1)

                    tile.tile_connections = neighbouring_tiles_pos

    def create_grid(self, stage: int = 0):
        self.stage = stage
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        self.tile_grid = [[Tile(tile_set=0, tile_type=0, tile_rotation=0) for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        self.tile_grid[self.grid_size_y//2][self.grid_size_x//2] = Tile(tile_set=2, tile_type=0, tile_rotation=0, unbreakable=True, connectable=True)

        self.add_factories()

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def add_factories(self):
        start_x, start_y = self.get_stage_size(0)
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        x_dif = (self.grid_size_x - start_x) // 2 + 1
        y_dif = (self.grid_size_y - start_y) // 2 + 1

        x_limit_low, x_limit_high = self.grid_size_x // 2 - x_dif // 2, self.grid_size_x // 2 + x_dif // 2
        y_limit_low, y_limit_high = self.grid_size_y // 2 - y_dif // 2, self.grid_size_y // 2 + y_dif // 2

        for _ in range(self.stage + 1):
            x, y = self.prn.generate() % self.grid_size_x, self.prn.generate() % self.grid_size_y
            while (x_limit_low <= x < x_limit_high and y_limit_low <= y < y_limit_high) or not (self.tile_grid[y][x].tile_set == 0 and self.tile_grid[y][x].tile_type == 0) or (self.prn.generate()%100/100) > (self.perlin_noise.value_at((self.grid_size_x / 2 - x + 0.5) / self.noise_scale, (self.grid_size_y / 2 - y + 0.5) / self.noise_scale) + 1) / 2:
                x, y = self.prn.generate() % self.grid_size_x, self.prn.generate() % self.grid_size_y

            self.tile_grid[y][x].tile_set = 2
            self.tile_grid[y][x].tile_type = 0
            self.tile_grid[y][x].tile_rotation = 0
            self.tile_grid[y][x].connectable = 1
            self.tile_grid[y][x].unbreakable = 1
            self.factories.append([x, y])

    def expand_grid(self):
        self.stage += 1
        old_x, old_y = self.grid_size_x, self.grid_size_y
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        x_dif = (self.grid_size_x - old_x) // 2
        y_dif = (self.grid_size_y - old_y) // 2

        old = self.tile_grid
        self.tile_grid = [[Tile(tile_set=0, tile_type=0, tile_rotation=0) for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        for y, row in enumerate(old):
            for x, tile in enumerate(row):
                self.tile_grid[y + y_dif][x + x_dif] = tile

        for effect in self.effects:
            effect.pos = effect.pos[0] + x_dif, effect.pos[1] + y_dif

        self.add_factories()

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def add_car(self):
        self.cars.append(Car())

    def add_effect(self):
        self.effects.append(Effect(pos=(self.grid_size_x // 2, self.grid_size_y // 2),length=0.25,num_stages=8))

    def decide_tile_type(self, tile_pos, center: bool = False):
        neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        neighbouring_tiles_pos = []
        neighbours_road = []
        num_connections = 0
        junctions = []

        for dx, dy in neighbours:
            junctions.append(False)
            neighbouring_tiles_pos.append([tile_pos[0] + dx, tile_pos[1] + dy])
            if 0 <= neighbouring_tiles_pos[-1][1] < self.grid_size_y and 0 <= neighbouring_tiles_pos[-1][0] < self.grid_size_x and (self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_set == 1 or self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].connectable):
                neighbours_road.append(1)
                num_connections += 1
                if self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_type > 3:
                    junctions.pop(-1)
                    junctions.append(True)
            else:
                neighbouring_tiles_pos.pop(-1)
                neighbours_road.append(0)

        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_connections = neighbouring_tiles_pos

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
                    tile.connectable = False
                    self.decide_tile_type(self.hover_tile_pos, True)
                    return True
                elif not del_ and tile.tile_set != 1:
                    tile.tile_set = 1
                    tile.connectable = True
                    self.decide_tile_type(self.hover_tile_pos, True)
                    return True

    def check_factory_clicked(self):
        if self.hover_tile_pos is not None and self.hover_tile_pos == (self.grid_size_x // 2, self.grid_size_y // 2):
            self.add_effect()
            return True

    def update(self, dt):
        tile_x, tile_y = self.screen_to_grid(pygame.mouse.get_pos())
        tile_x, tile_y = int(tile_x), int(tile_y)
        if 0 <= tile_x < self.grid_size_x and 0 <= tile_y < self.grid_size_y:
            self.hover_tile_pos = tile_x, tile_y
        else:
            self.hover_tile_pos = None

        for effect in self.effects:
            effect.time += dt
            effect.stage = int(effect.time / effect.length * effect.num_stages)
            if effect.stage >= effect.num_stages:
                self.effects.remove(effect)

    def draw(self, show_hover = True, path = None):
        top_left_tile_pos = self.screen_to_grid((0, 0))
        bottom_right_tile_pos = self.screen_to_grid((screen.WIN.get_width(), screen.WIN.get_height()))

        for y, row in enumerate(self.tile_grid):
            for x, tile in enumerate(row):
                screen_x, screen_y = self.grid_to_screen((x, y))
                if -self.scaled_tile_size <= screen_x < screen.WIN.get_width() and -self.scaled_tile_size <= screen_y < screen.WIN.get_height():
                    screen.WIN.blit(self.scaled_images[tile.tile_set][tile.tile_type][tile.tile_rotation], (screen_x, screen_y))
                    # screen.WIN.blit(self.scaled_car, (screen_x + self.scaled_tile_size_half, screen_y))

                    if path is not None and [x, y] in path:
                        pygame.draw.circle(screen.WIN, (255, 50, 50), (screen_x, screen_y), 5)

                    # val = (self.perlin_noise.value_at((self.grid_size_x / 2 - x + 0.5) / self.noise_scale, (self.grid_size_y / 2 - y + 0.5) / self.noise_scale) + 1) / 2
                    # pygame.draw.circle(screen.WIN, (255 * val, 255 * val, 255 * val), (screen_x + self.scaled_tile_size_half, screen_y + self.scaled_tile_size_half), 4)

        for effect in self.effects:
            x, y = self.grid_to_screen(effect.pos)
            screen.WIN.blit(self.scaled_images_effect[effect.stage], (x, y))

        if show_hover:
            if self.hover_tile_pos is not None:
                x, y = self.grid_to_screen(self.hover_tile_pos)
                screen.WIN.blit(self.scaled_image_hover, (x, y))
            screen.WIN.blit(self.image_build_mode, (10, 10))
