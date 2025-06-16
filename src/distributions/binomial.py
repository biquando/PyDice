from custom_distribution import CustomDistribution
from dicetypes import DiceType, IntType
import random

class BinomialDistribution(CustomDistribution):
    NAME = "binomial"
    ARG_TYPES = (int, int, float)

    def __init__(self, width, n, p):
        self.width = width
        self.n = n
        self.p = p

    def sample(self) -> DiceType:
        n_successes = 0
        for _ in range(self.n):
            if random.random() < self.p:
                n_successes += 1
        return IntType(self.width, n_successes)
