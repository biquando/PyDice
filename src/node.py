import log
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
        self.prob = prob

    def __repr__(self):
        return f"FlipNode({self.prob})"


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


### Unary operations ###########################################################


class UnaryNode(ExprNode):
    def __init__(self, operand: ExprNode):
        self.operand = operand
        self.op = lambda _: None

    def __repr__(self):
        return "(\n" + log.indent(self.operand) + "\n" + ")"


class NotNode(UnaryNode):
    def __init__(self, operand: ExprNode):
        super().__init__(operand)
        self.op = operator.not_

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
            "(\n" + log.indent(self.left) + ",\n" + log.indent(self.right) + "\n" + ")"
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
