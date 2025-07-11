# Required to use type annotations within own class
from __future__ import annotations


class DiceType:
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"DiceType({self.val})"

    def __hash__(self):
        return hash(self.val)

    def __eq__(self, other):
        return BoolType(isinstance(other, DiceType) and self.val == other.val)


class BoolType(DiceType):
    def __init__(self, val: bool):
        super().__init__(val)

    def __repr__(self):
        return f"BoolType({self.val})"

    def verify_types(self, other: BoolType):
        if type(other) is not BoolType:
            raise TypeError(
                f"Boolean operation must act on two booleans ({type(other)})"
            )

    def __and__(self, other: BoolType) -> BoolType:
        self.verify_types(other)
        return BoolType(self.val and other.val)

    def __or__(self, other: BoolType) -> BoolType:
        self.verify_types(other)
        return BoolType(self.val or other.val)

    def __not__(self) -> BoolType:
        return BoolType(not self.val)


class IntType(DiceType):
    def __init__(self, width: int, val: int):
        if width <= 0:
            raise ValueError("Int width should be at least one bit")
        self.width = width
        super().__init__(val % (2**self.width))

    def __repr__(self):
        return f"IntType({self.width}, {self.val})"

    def verify_types(self, other: IntType):
        if type(other) is not IntType:
            raise TypeError("Integer operation must act on two integers")
        if self.width != other.width:
            raise TypeError(
                f"Integer operands must be equal widths ({self.width} != {other.width})"
            )

    def __lt__(self, other: IntType) -> BoolType:
        self.verify_types(other)
        return BoolType(self.val < other.val)

    def __add__(self, other: IntType) -> IntType:
        self.verify_types(other)
        return IntType(self.width, self.val + other.val)

    def __sub__(self, other: IntType) -> IntType:
        self.verify_types(other)
        return IntType(self.width, self.val - other.val)

    def __mul__(self, other: IntType) -> IntType:
        self.verify_types(other)
        return IntType(self.width, self.val * other.val)

    def __floordiv__(self, other: IntType) -> IntType:
        self.verify_types(other)
        return IntType(self.width, self.val // other.val)

    def __lshift__(self, other: int) -> IntType:
        if type(other) is not int:
            raise TypeError(f"Must left shift by an int literal (found {type(other)})")
        return IntType(self.width, self.val << other)

    def __rshift__(self, other: int) -> IntType:
        if type(other) is not int:
            raise TypeError(f"Must left shift by an int literal (found {type(other)})")
        return IntType(self.width, self.val >> other)


class TupleType(DiceType):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def fst(self):
        return self.left

    def snd(self):
        return self.snd

    def __repr__(self):
        return f"TupleType({self.left}, {self.right})"

    def __hash__(self):
        return hash(hash(self.left) + hash(self.right))

    def __eq__(self, other):
        return BoolType(
            isinstance(other, TupleType)
            and self.left == other.left
            and self.right == other.right
        )


class ListType(DiceType):
    def __init__(self, lst, type_):
        self.lst = lst
        self.type_ = type_

    def __repr__(self):
        return f"ListType({', '.join((str(itm) for itm in self.lst))})"

    def __hash__(self):
        return hash("".join((str(itm) for itm in self.lst)))

    def __eq__(self, other):
        return BoolType(
            isinstance(other, ListType) 
            and len(self.lst) == len(other.lst)
            and all((left == right for left, right in zip(self.lst, other.lst)))
        )
