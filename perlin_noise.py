import math

import pygame
from math import cos, sin, radians
from dataclasses import dataclass


@dataclass
class Vector:
    x: float = 0
    y: float = 0
    z: float = 0

    def add(self, other: "Vector"):
        self.x += other.x
        self.y += other.y
        self.z += other.z


class PerlinNoise2D:
    def __init__(self, seed: int):
        self.seed = seed

    @staticmethod
    def vector_at(x: float, y: float, seed: int):
        modulus = 7435823353535
        multiplier = 2336077154641
        increment = 4876216402987

        if seed < 0 or seed > modulus:
            raise Exception("seed error")

        angle = (multiplier * (seed - x * y) + increment) % modulus
        angle = (multiplier * angle + increment) % 360

        return Vector(x=cos(radians(angle)), y=sin(radians(angle)))

    @staticmethod
    def interpolate(a, b, w):
        # return (b - a) * w + a
        return (b - a) * (3.0 - w * 2.0) * w * w + a

    @staticmethod
    def dot_product(v1, v2):
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def dot_product_at(gx: float, gy: float, x: float, y: float, seed: int):
        gradient = PerlinNoise2D.vector_at(gx, gy, seed)

        dv = Vector(x=(x - gx), y=(y - gy))

        return PerlinNoise2D.dot_product(gradient, dv)

    def value_at(self, x: float, y: float):
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        d0 = self.dot_product_at(x0, y0, x, y, self.seed)
        d1 = self.dot_product_at(x1, y0, x, y, self.seed)
        ix0 = self.interpolate(d0, d1, x - x0)

        d0 = self.dot_product_at(x0, y1, x, y, self.seed)
        d1 = self.dot_product_at(x1, y1, x, y, self.seed)
        ix1 = self.interpolate(d0, d1, x - x0)

        value = self.interpolate(ix0, ix1, y - y0)

        return value


class PerlinNoise3D:
    def __init__(self, seed: int):
        self.seed = seed

    @staticmethod
    def vector_at(x: float, y: float, z:float, seed: int):
        modulus = 7435823353535243523453
        multiplier = 2336077154641345234523
        increment = 4876216402987643562345

        if seed < 0 or seed > modulus:
            raise Exception("seed error")

        angle = (multiplier * (seed - x * y * z) + increment) % modulus
        angle = (multiplier * angle + increment) % 360

        return Vector(x=cos(radians(angle)), y=sin(radians(angle)))

    @staticmethod
    def interpolate(a, b, w):
        # return (b - a) * w + a
        return (b - a) * (3.0 - w * 2.0) * w * w + a

    @staticmethod
    def dot_product(v1, v2):
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def dot_product_at(gx: float, gy: float, gz:float, x: float, y: float, seed: int):
        gradient = PerlinNoise3D.vector_at(gx, gy, gz, seed)

        dv = Vector(x=(x - gx), y=(y - gy))

        return PerlinNoise2D.dot_product(gradient, dv)

    def value_at(self, x: float, y: float, z: float):
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1
        z0 = math.floor(z)
        z1 = z0 + 1

        d0 = self.dot_product_at(x0, y0, z0, x, y, self.seed)
        d1 = self.dot_product_at(x1, y0, z0, x, y, self.seed)
        ix0 = self.interpolate(d0, d1, x - x0)

        d0 = self.dot_product_at(x0, y1, z0, x, y, self.seed)
        d1 = self.dot_product_at(x1, y1, z0, x, y, self.seed)
        ix1 = self.interpolate(d0, d1, x - x0)

        iy0 = self.interpolate(ix0, ix1, y - y0)

        d0 = self.dot_product_at(x0, y0, z1, x, y, self.seed)
        d1 = self.dot_product_at(x1, y0, z1, x, y, self.seed)
        ix0 = self.interpolate(d0, d1, x - x0)

        d0 = self.dot_product_at(x0, y1, z1, x, y, self.seed)
        d1 = self.dot_product_at(x1, y1, z1, x, y, self.seed)
        ix1 = self.interpolate(d0, d1, x - x0)

        iy1 = self.interpolate(ix0, ix1, y - y0)

        value = self.interpolate(iy0, iy1, z - z0)

        return value


# if __name__ == '__main__':
#     p = PerlinNoise2D(int(input("SEED: ")))
#     grid_size = int(input("GRID: "))
#     pygame.init()
#
#     win = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
#
#     while 1:
#         for x in range(1920):
#             for y in range(1080):
#                 for e in pygame.event.get():
#                     if e.type == pygame.QUIT:
#                         quit()
#                 pygame.event.clear()
#
#                 v = (p.value_at(x / grid_size, y / grid_size) + 1) / 2
#                 win.set_at((x, y), (255 * v, 0, 255 * (1-v)))
#
#             pygame.display.flip()
#
#         p.seed = (p.seed + 12341) % 7435823353535

# if __name__ == '__main__':
#     p = PerlinNoise2D(int(input("SEED: ")))
#     pygame.init()
#
#     win = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
#
#     class Particle:
#         def __init__(self, x, y):
#             self.pos = Vector(x=x, y=y)
#             self.vel = Vector(x=0, y=0)
#             self.acc = Vector(x=0, y=0)
#
#         def update(self):
#             self.vel.add(self.acc)
#             self.pos.add(self.vel)
#
#
#     while 1:
#         win.fill((0, 0, 0))
#
#         for x in range(191):
#             for y in range(107):
#                 for e in pygame.event.get():
#                     if e.type == pygame.QUIT:
#                         quit()
#                 pygame.event.clear()
#
#                 v = (p.value_at(x / 10 + 0.5, y / 10 + 0.5) + 1) * 360
#                 pygame.draw.line(win, (255, 255, 255), (x * 10 + 10, y * 10 + 10), (x * 10 + 10 + cos(radians(v)) * 10, y * 10 + 10 + sin(radians(v)) * 10))
#
#         pygame.display.flip()
#
#         p.seed = (p.seed + 12341) % 7435823353535


# if __name__ == '__main__':
#     p = PerlinNoise2D(int(input("SEED: ")))
#     grid_size = int(input("GRID: "))
#
#     pygame.init()
#
#     win = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
#
#     while 1:
#         win.fill((0, 0, 0))
#
#         for x in range(191):
#             for y in range(107):
#                 for e in pygame.event.get():
#                     if e.type == pygame.QUIT:
#                         quit()
#                 pygame.event.clear()
#
#                 v = (p.value_at(x / grid_size, y / grid_size) + 1) / 2
#                 pygame.draw.circle(win, (255, 255, 255), ((x+1) * grid_size, (y+1) * grid_size), v*25)
#
#         pygame.display.flip()
#
#         p.seed = (p.seed + 12341) % 7435823353535

if __name__ == '__main__':
    p = PerlinNoise3D(int(input("SEED: ")))
    pygame.init()

    x_size, y_size = 100, 100
    x_zoom, y_zoom = 10, 10
    SIZE = WIDTH, HEIGHT = 1920, 1080

    win = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    z = 0

    while 1:
        win.fill((0, 0, 0))

        for x in range(x_size - 1):
            for y in range(y_size - 1):
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        quit()
                pygame.event.clear()

                v = (p.value_at(x / x_zoom + 0.5, y / y_zoom + 0.5, z) + 1) * 540
                pygame.draw.line(win, (255, 255, 255), ((x + 1) * WIDTH / x_size, (y + 1) * HEIGHT / y_size), ((x + 1) * WIDTH / x_size + cos(radians(v)) * WIDTH / x_size, (y + 1) * HEIGHT / y_size + sin(radians(v)) * HEIGHT / y_size))

        pygame.display.flip()

        z += 0.1
