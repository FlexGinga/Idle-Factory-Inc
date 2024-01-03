from dataclasses import dataclass

@dataclass
class Upgrade:
    title: str
    price: int
    desc: str
    func: "function"

    activated: bool = False
    pressed: bool = False
