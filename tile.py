from dataclasses import dataclass

@dataclass
class Tile:
    tile_set: int
    tile_type: int
    tile_rotation: int

    occupied: list
    occupied_action: list

    tile_connections: list = ()

    unbreakable: bool = False
    connectable: bool = False

    def reset_occupation(self):
        self.occupied = [False, False, False, False]
        self.occupied_action = [None, None, None, None]
