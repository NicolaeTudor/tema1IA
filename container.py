from dataclasses import dataclass, field


@dataclass
class Container:
    max_cap: int = field(compare=False)
    occupied: int
    color: int

    def __hash__(self):
        return hash((self.occupied, self.color))


