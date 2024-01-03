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
        self.factories = []

        self.images = []
        self.image_hover = None
        self.image_error = None
        self.images_effect = []

        self.scaled_images = []
        self.scaled_image_hover = None
        self.scaled_image_error = None
        self.scaled_images_effect = []

        self.image_car = None
        self.scaled_cars = [None, None, None, None]

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

        self.create_grid()

        self.cars = []
        self.cars_waiting = [[], []]

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

        self.image_hover = pygame.image.load("assets/map/hover.png").convert_alpha()
        self.image_error = pygame.image.load("assets/map/error.png").convert_alpha()

        path = "assets/map/effect/"
        for effect in listdir(path):
            effect_set = []
            scaled_effect = []
            for image in listdir(path + effect):
                effect_set.append(pygame.image.load(path + effect + "/" + image).convert_alpha())
                scaled_effect.append(None)
            self.images_effect.append(effect_set)
            self.scaled_images_effect.append(scaled_effect)

        self.image_car = pygame.image.load("assets/cars/truck.png").convert_alpha()

        self.image_build_mode = pygame.transform.scale(pygame.image.load("assets/map/build_mode_icon.png").convert_alpha(), (48,32))


    def scale_images(self):
        size = (self.scaled_tile_size, self.scaled_tile_size)
        for i, image_set in enumerate(self.images):
            for j, rotation_set in enumerate(image_set):
                for k, image in enumerate(rotation_set):
                    self.scaled_images[i][j][k] = pygame.transform.scale(image, size)

        self.scaled_image_hover = pygame.transform.scale(self.image_hover, size)
        self.scaled_image_error = pygame.transform.scale(self.image_error, size)

        for i, effect in enumerate(self.images_effect):
            for j, image in enumerate(effect):
                self.scaled_images_effect[i][j] = pygame.transform.scale(image, size)

        size = size[0] / 5, size[1] / 2.5
        for i in range(4):
            self.scaled_cars[i] = pygame.transform.rotate(pygame.transform.scale(self.image_car, size), 90 * -i)

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

    def reset_offset(self):
        self.offset_x = 0
        self.offset_y = 0

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

    def check_neighbours(self, pos):
        sets = []
        types = []

        neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        x, y = pos
        for dx, dy in neighbours:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size_x and 0 <= ny < self.grid_size_y:
                sets.append(self.tile_grid[ny][nx].tile_set)
                types.append(self.tile_grid[ny][nx].tile_type)
            else:
                sets.append(None)
                types.append(None)

        return sets, types

    def create_grid(self, stage: int = 0):
        self.stage = stage
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        self.tile_grid = [[None for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        for y in range(self.grid_size_y):
            for x in range(self.grid_size_x):
                self.tile_grid[y][x] = Tile(tile_set=0, tile_type=0, tile_rotation=0, occupied=[False, False, False, False], occupied_action=[None, None, None, None])
        self.tile_grid[self.grid_size_y//2][self.grid_size_x//2] = Tile(tile_set=2, tile_type=0, tile_rotation=0, unbreakable=True, connectable=True, occupied=[False, False, False, False], occupied_action=[None, None, None, None])

        self.add_factories()

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def add_factories(self):
        start_x, start_y = self.get_stage_size(0)
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        x_dif = (self.grid_size_x - start_x) // 2 + 1
        y_dif = (self.grid_size_y - start_y) // 2 + 1

        x_limit_low, x_limit_high = x_dif, self.grid_size_x - x_dif
        y_limit_low, y_limit_high = y_dif, self.grid_size_y - y_dif

        for _ in range(self.stage + 1):
            x, y = self.prn.generate() % self.grid_size_x, self.prn.generate() % self.grid_size_y
            while (x_limit_low <= x < x_limit_high and y_limit_low <= y < y_limit_high) or not (self.tile_grid[y][x].tile_set == 0 and self.tile_grid[y][x].tile_type == 0) or 2 in self.check_neighbours([x, y])[0] or (self.prn.generate()%100/100) > (self.perlin_noise.value_at((self.grid_size_x / 2 - x + 0.5) / self.noise_scale, (self.grid_size_y / 2 - y + 0.5) / self.noise_scale) + 1) / 2:
                x, y = self.prn.generate() % self.grid_size_x, self.prn.generate() % self.grid_size_y

            self.tile_grid[y][x].tile_set = 2
            self.tile_grid[y][x].tile_type = 0
            self.tile_grid[y][x].tile_rotation = 0
            self.tile_grid[y][x].connectable = 1
            self.tile_grid[y][x].unbreakable = 1
            self.factories.append([[x, y], 0])

    def expand_grid(self):
        self.stage += 1
        old_x, old_y = self.grid_size_x, self.grid_size_y
        self.grid_size_x, self.grid_size_y = self.get_stage_size(self.stage)

        x_dif = (self.grid_size_x - old_x) // 2
        y_dif = (self.grid_size_y - old_y) // 2

        old = self.tile_grid
        self.tile_grid = [[Tile(tile_set=0, tile_type=0, tile_rotation=0, occupied=[False, False, False, False], occupied_action=[None, None, None, None]) for _ in range(self.grid_size_x)] for _ in range(self.grid_size_y)]
        for y, row in enumerate(old):
            for x, tile in enumerate(row):
                self.tile_grid[y + y_dif][x + x_dif] = tile

        for effect in self.effects:
            effect.pos = effect.pos[0] + x_dif, effect.pos[1] + y_dif

        for car in self.cars:
            for pos in car.path:
                pos[0] += x_dif
                pos[1] += y_dif

        for type_ in self.cars_waiting:
            for car in type_:
                for pos in car.path:
                    pos[0] += x_dif
                    pos[1] += y_dif

        for factory in self.factories:
            factory[0][0] += x_dif
            factory[0][1] += y_dif

        self.add_factories()

        for y, row in enumerate(self.tile_grid):
            for x, tile in enumerate(row):
                self.decide_tile_type([x, y])

        self.offset_constant_x = self.scaled_tile_size * self.grid_size_x // 2
        self.offset_constant_y = self.scaled_tile_size * self.grid_size_y // 2

    def find_least_populated_factory(self):
        acceptable = False
        smallest_index = -1
        for i, factory in enumerate(self.factories):
            if (factory[1] < self.factories[smallest_index][1] or smallest_index == -1) and factory[1] < 5 and AStar.find_path(self.tile_grid, [self.grid_size_x // 2, self.grid_size_y // 2], factory[0], self.prn) != []:
                acceptable = True
                smallest_index = i
        return smallest_index, acceptable

    def add_car(self):
        factory_index, accepted = self.find_least_populated_factory()
        if accepted:
            self.cars.append(Car(AStar.find_path(self.tile_grid, [self.grid_size_x // 2, self.grid_size_y // 2], self.factories[factory_index][0], self.prn), False))
            self.factories[factory_index][1] += 1
        return accepted

    def add_effect(self, pos, type_, length):
        num_stages = len(self.scaled_images_effect[type_])
        self.effects.append(Effect(pos=pos,type=type_,length=length,num_stages=num_stages))

    def get_tile_neighbours(self, tile_pos):
        neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        neighbouring_tiles_pos = []
        neighbours_road = []
        num_connections = 0

        for dx, dy in neighbours:
            neighbouring_tiles_pos.append([tile_pos[0] + dx, tile_pos[1] + dy])
            if 0 <= neighbouring_tiles_pos[-1][1] < self.grid_size_y and 0 <= neighbouring_tiles_pos[-1][
                0] < self.grid_size_x and (
                    self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_set == 1 or
                    self.tile_grid[neighbouring_tiles_pos[-1][1]][neighbouring_tiles_pos[-1][0]].tile_set == 2):
                neighbours_road.append(1)
                num_connections += 1
            else:
                neighbouring_tiles_pos.pop(-1)
                neighbours_road.append(0)

        return neighbouring_tiles_pos, neighbours_road, num_connections

    def decide_tile_type(self, tile_pos, center: bool = False):
        neighbouring_tiles_pos,neighbours_road, num_connections = self.get_tile_neighbours(tile_pos)

        self.tile_grid[tile_pos[1]][tile_pos[0]].tile_connections = neighbouring_tiles_pos

        old_type = self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type
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

        if center or old_type != self.tile_grid[tile_pos[1]][tile_pos[0]].tile_type:
            for pos in neighbouring_tiles_pos:
                if self.tile_grid[pos[1]][pos[0]].connectable:
                    self.decide_tile_type(pos)

    def check_tile_use(self, pos):
        for car in self.cars:
            if pos in car.path[car.path_index:]:
                return True
        return False

    def on_click(self, del_: bool = False):
        if self.hover_tile_pos is not None:
            tile = self.tile_grid[self.hover_tile_pos[1]][self.hover_tile_pos[0]]
            if not tile.unbreakable:
                if del_ and tile.tile_set == 1 and not self.check_tile_use(self.hover_tile_pos):
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
        if self.hover_tile_pos is not None and self.hover_tile_pos == [self.grid_size_x // 2, self.grid_size_y // 2]:
            self.add_effect((self.grid_size_x // 2, self.grid_size_y // 2), 0, 0.25)
            return True

    def reset_cars(self):
        for car in self.cars:
            if car.path_index != 0:
                x, y = car.path[car.path_index]
                self.tile_grid[y][x].occupied[car.prev_direction] = False
                self.tile_grid[y][x].occupied_action[car.prev_direction] = None

            if not car.to_hub:
                car.path = [car.path[-1], car.path[0]]
            self.cars_waiting[1].append(car)
        self.cars = []

    def update(self, dt, car_speed, paused: bool = False):
        tile_x, tile_y = self.screen_to_grid(pygame.mouse.get_pos())
        tile_x, tile_y = int(tile_x), int(tile_y)
        if 0 <= tile_x < self.grid_size_x and 0 <= tile_y < self.grid_size_y:
            self.hover_tile_pos = [tile_x, tile_y]
        else:
            self.hover_tile_pos = None

        if not paused:
            for i, type_ in enumerate(self.cars_waiting):
                for car in type_:
                    path = AStar.find_path(self.tile_grid, car.path[-1], car.path[0], self.prn)
                    if path:
                        car.reset(path, bool(i), bool(i))
                        self.cars.append(car)
                        self.cars_waiting[i].remove(car)

        completed_trips = 0
        for car in self.cars:
            path_x, path_y = car.path[car.path_index + 1]

            if car.path_index + 1 == len(car.path) - 1 or (not self.tile_grid[path_y][path_x].occupied[car.get_next_direction()] and
                                                            (
                                                                    self.tile_grid[path_y][path_x].tile_type < 4 or
                                                                    (self.tile_grid[path_y][path_x].tile_type == 4 and (True not in self.tile_grid[path_y][path_x].occupied or self.tile_grid[path_y][path_x].occupied.count(True) == 1 and self.tile_grid[path_y][path_x].occupied[(car.get_next_direction() + 2) % 4] and car.get_action(1) == 1 and self.tile_grid[path_y][path_x].occupied_action[(car.get_next_direction() + 2) % 4] == 1))
                                                            )
            ):
                car.state = 1
            else:
                car.state = 0
                car.set_deceleration_amount()


            match car.update(dt, car_speed):
                case 1:
                    old_x, old_y = car.path[car.path_index - 1]
                    self.tile_grid[old_y][old_x].occupied[car.prev_direction] = False
                    self.tile_grid[old_y][old_x].occupied_action[car.prev_direction] = None
                    new_x, new_y = car.path[car.path_index]
                    self.tile_grid[new_y][new_x].occupied[car.direction] = True
                    self.tile_grid[new_y][new_x].occupied[car.direction] = car.get_action(car.direction)

                case 2:
                    old_x, old_y = car.path[car.path_index - 1]
                    self.tile_grid[old_y][old_x].occupied[car.prev_direction] = False
                    self.tile_grid[old_y][old_x].occupied_action[car.prev_direction] = None
                    if car.to_hub:
                        if car.been_to_factory:
                            completed_trips += 1

                        path = AStar.find_path(self.tile_grid, car.path[-1], car.path[0], self.prn)
                        if path:
                            car.reset(path, False, False)
                            new_x, new_y = car.path[car.path_index]
                            self.tile_grid[new_y][new_x].occupied[car.direction] = True
                            self.tile_grid[new_y][new_x].occupied[car.direction] = car.get_action(car.direction)
                        else:
                            self.add_effect(car.path[0], 1, 2)
                            self.cars_waiting[0].append(car)
                            self.cars.remove(car)

                    else:
                        path = AStar.find_path(self.tile_grid, car.path[-1], car.path[0], self.prn)

                        if path:
                            car.reset(path, True, True)
                            new_x, new_y = car.path[car.path_index]
                            self.tile_grid[new_y][new_x].occupied[car.direction] = True
                            self.tile_grid[new_y][new_x].occupied[car.direction] = car.get_action(car.direction)
                        else:
                            self.add_effect(car.path[-1], 1, 2)
                            self.cars_waiting[1].append(car)
                            self.cars.remove(car)

        for effect in self.effects:
            effect.time += dt
            effect.stage = int(effect.time / effect.length * effect.num_stages)
            if effect.stage >= effect.num_stages:
                self.effects.remove(effect)

        return completed_trips

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

        for car in self.cars:
            x, y = self.grid_to_screen(car.path[car.path_index])

            x += car.relative_x * self.scaled_tile_size
            y += (1 - car.relative_y) * self.scaled_tile_size
            img = self.scaled_cars[car.relative_direction]
            screen.WIN.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

        for effect in self.effects:
            x, y = self.grid_to_screen(effect.pos)
            screen.WIN.blit(self.scaled_images_effect[effect.type][effect.stage], (x, y))

        if show_hover:
            if self.hover_tile_pos is not None:
                x, y = self.grid_to_screen(self.hover_tile_pos)
                screen.WIN.blit(self.scaled_image_hover, (x, y))
            screen.WIN.blit(self.image_build_mode, (10, 10))
