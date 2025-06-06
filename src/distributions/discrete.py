from custom_distribution import CustomDistribution
from dicetypes import DiceType, IntType
import math
import random

class DiscreteDistribution(CustomDistribution):
    NAME = "discrete"
    ARG_TYPES = (list[float],)
    # These can be int, float, list[int], or list[float]

    def __init__(self, probs: list[float]):
        for prob in probs:
            if prob < 0:
                raise ValueError(f"Invalid discrete probability ({prob})")

        # Extend length to power of two
        bit_width = math.ceil(math.log2(len(probs)))
        new_len = 2 ** bit_width
        probs += [0.] * (new_len - len(probs))

        # Normalize
        #  The original Dice does not allow for distributions that don't add
        #  up to one. In PyDice, we normalize the input probabilities, allowing
        #  the user to input any nonnegative weights, which then get normalized
        #  to a valid probability distribution.
        total = sum(probs)
        probs = [prob / total for prob in probs]

        self.bit_width = bit_width
        self.probs = probs

    def sample(self) -> DiceType:
        r = random.random()
        accumulated_prob = 0.0
        for i, prob in enumerate(self.probs):
            accumulated_prob += prob
            if r < accumulated_prob:
                return IntType(self.bit_width, i)
        assert False
