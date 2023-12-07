from dataclasses import dataclass

@dataclass
class Tile:
    tile_set: int
    tile_type: int
    tile_rotation: int

    unbreakable: bool = False
    connectable: bool = True
