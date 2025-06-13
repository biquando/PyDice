from custom_distribution import CustomDistribution
from dicetypes import DiceType, IntType
import random

class UniformDistribution(CustomDistribution):
    NAME = "uniform"
    ARG_TYPES = (int, int, int)
    # These can be int, float, list[int], or list[float]

    def __init__(self, size: int, start: int, end: int):
        if start >= 2 ** size:
            raise ValueError("Empty uniform distribution")
        if end <= start:
            raise ValueError("End must be greater than start")

        self.size = size
        self.start = start
        self.end = end

    def sample(self) -> DiceType:
        options = range(self.start, self.end)
        choice = random.choice(options)
        return IntType(self.size, choice)
