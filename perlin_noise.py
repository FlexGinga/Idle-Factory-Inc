import math
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
    def vector_at(x: float, y: float, seed: int): #  generates a pseudorandom 2d vector at a point based on the seed
        modulus = 959857733253590491001078404603612020793228588850354911013633616918542968975259052960484550138938520872388476718109276380890630691369515120381467006418691149911156674895378040944334942091085462649060087281872150108197816980147220510650915109520425193185117
        multiplier = 616354853510616026187719200236569457260014603696329969884148660275164751955627594513978619236612387569342601264104586368066007954466871725866842744123769200541865064382514967438966074361856811582055187583531445212426607420158975393893066943046888669498281
        increment = 859701557052794370761469115252871089237500470683061849414666236943212017515272296341620012156223675182045418994675275566497526842804976038157284321768425203411123255752636935475937674298350695067209549311497649409835903393145624161001439493455881581542989

        if seed < 0 or seed > modulus:
            raise Exception("seed error")

        angle = (multiplier * (seed * x - y) + increment) % modulus
        angle = (multiplier * angle + increment) % 360

        return Vector(x=cos(radians(angle)), y=sin(radians(angle)))

    @staticmethod
    def interpolate(a, b, w): #  generates a smooth transition between 2 values. w is the weight that determines influence of adjacent points
        # return (b - a) * w + a
        return (b - a) * (3.0 - w * 2.0) * w * w + a

    @staticmethod
    def dot_product(v1, v2): #  generates single value from multiple vectors
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def dot_product_at(gx: float, gy: float, x: float, y: float, seed: int): #  implementation of the dot product function
        gradient = PerlinNoise2D.vector_at(gx, gy, seed)

        dv = Vector(x=(x - gx), y=(y - gy))

        return PerlinNoise2D.dot_product(gradient, dv)

    def value_at(self, x: float, y: float): # generates the noise value at a specific point
        #  creates integer points for the corners of the perlin noise grid the inputted point is located
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1


        d0 = self.dot_product_at(x0, y0, x, y, self.seed) #  generate value from top left corner
        d1 = self.dot_product_at(x1, y0, x, y, self.seed) #  generate value from top right corner
        ix0 = self.interpolate(d0, d1, x - x0)

        d0 = self.dot_product_at(x0, y1, x, y, self.seed) #  generate value from bottom left corner
        d1 = self.dot_product_at(x1, y1, x, y, self.seed) #  generate value from bottom right corner
        ix1 = self.interpolate(d0, d1, x - x0)

        value = self.interpolate(ix0, ix1, y - y0)

        return value


if __name__ == '__main__':
    import pygame

    pygame.init()

    win = pygame.display.set_mode((1920, 1080))

    pn = PerlinNoise2D(4535)

    while 1:
        for x in range(1920):
            for y in range(1080):
                val = (pn.value_at((x + 0.5) / 200, (y + 0.5) / 200) + 1) / 2
                win.set_at((x, y), (255 * val, 255 * val, 255 * val))
            pygame.display.flip()
