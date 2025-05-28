import log
import math
import operator


class Node: ...


class ExprNode(Node): ...


class IdentNode(ExprNode):
    def __init__(self, ident: str):
        self.ident = ident

    def __repr__(self):
        return f'IdentNode("{self.ident}")'


class FlipNode(ExprNode):
    def __init__(self, prob: float):
        if prob < 0 or prob > 1:
            raise ValueError(f"Invalid flip probability ({prob})")
        self.prob = prob

    def __repr__(self):
        return f"FlipNode({self.prob})"


class DiscreteNode(ExprNode):
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

    def __repr__(self):
        return f"DiscreteNode({self.probs})"


class AssignNode(ExprNode):
    def __init__(self, ident: str, val: ExprNode, rest: ExprNode):
        self.ident = ident
        self.val = val
        self.rest = rest

    def __repr__(self):
        return (
            "AssignNode(\n"
            + log.indent(f"{self.ident} = {self.val};\n")
            + log.indent(self.rest)
            + "\n"
            + ")"
        )

class IfNode(ExprNode):
    def __init__(self, cond: ExprNode, true_expr: ExprNode, false_expr: ExprNode):
        self.cond = cond
        self.true_expr = true_expr
        self.false_expr = false_expr

    def __repr__(self):
        return (
            "AssignNode(\n"
            + log.indent(self.cond)+"\n"
            + log.indent(self.true_expr)+"\n"
            + log.indent(self.false_expr)+"\n"
            + ")"
        )

### Unary operations ###########################################################


class UnaryNode(ExprNode):
    def __init__(self, operand: ExprNode):
        self.operand = operand
        self.op = lambda _: None

    def __repr__(self):
        return (
            "(\n"
            + log.indent(self.operand)
            + "\n)"
        )


class NotNode(UnaryNode):
    def __init__(self, operand: ExprNode):
        super().__init__(operand)
        self.op = lambda x: x.__not__() # can't override not operator for object

    def __repr__(self):
        return "NotNode" + super().__repr__()


### Binary operations ##########################################################


class BinaryNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right
        self.op = lambda _, __: None

    def __repr__(self):
        return (
            "(\n"
            + log.indent(self.left)
            + ",\n"
            + log.indent(self.right)
            + "\n)"
        )


class AndNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.and_

    def __repr__(self):
        return "AndNode" + super().__repr__()


class OrNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.or_

    def __repr__(self):
        return "OrNode" + super().__repr__()

class AddNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.add

    def __repr__(self):
        return "AddNode" + super().__repr__()

class SubNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.sub

    def __repr__(self):
        return "SubNode" + super().__repr__()

class MulNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.mul

    def __repr__(self):
        return "MulNode" + super().__repr__()

class DivNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.floordiv

    def __repr__(self):
        return "DivNode" + super().__repr__()
