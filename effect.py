from dataclasses import dataclass

@dataclass
class Effect:
    pos: tuple

    type: int
    length: float
    num_stages: int

    time: float = 0
    stage: int = 0
