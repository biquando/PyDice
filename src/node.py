import log
import math
import operator
from dicetypes import DiceType


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
            "IfNode(\n"
            + log.indent(self.cond)
            + "\n"
            + log.indent(self.true_expr)
            + "\n"
            + log.indent(self.false_expr)
            + "\n"
            + ")"
        )


class ObserveNode(ExprNode):
    def __init__(self, observation: ExprNode):
        self.observation = observation

    def __repr__(self):
        return "ObserveNode(\n" + log.indent(self.observation) + "\n" + ")"


### Unary operations ###########################################################


class UnaryNode(ExprNode):
    def __init__(self, operand: ExprNode):
        self.operand = operand
        self.op = lambda _: None

    def __repr__(self):
        return "(\n" + log.indent(self.operand) + "\n)"


class NotNode(UnaryNode):
    def __init__(self, operand: ExprNode):
        super().__init__(operand)
        self.op = lambda x: x.__not__()  # can't override not operator for object

    def __repr__(self):
        return "NotNode" + super().__repr__()


### Binary operations ##########################################################


class BinaryNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right
        self.op = lambda _, __: None

    def __repr__(self):
        return "(\n" + log.indent(self.left) + ",\n" + log.indent(self.right) + "\n)"


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


class EqualNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.eq

    def __repr__(self):
        return "EqualNode" + super().__repr__()


class LessThanNode(BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
        self.op = operator.lt

    def __repr__(self):
        return "LessThanNode" + super().__repr__()


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


### Function Nodes ##########################################################


class ProgramNode(Node):
    def __init__(self, nodes):
        self.functions = []

        n = len(nodes)
        for i in range(n):
            if i == n - 1:
                self.expr = nodes[i]
            else:
                self.functions.append(nodes[i])

    def __repr__(self):
        return f'ProgramNode("{self.functions},{self.expr}")'


class TypeNode(Node): ...


class ArgNode(Node):
    def __init__(self, ident: str, data_type: DiceType):
        self.ident = ident
        self.type = data_type

    def __repr__(self):
        return f'ArgNode("{self.ident},{self.type}")'


class ArgListNode(Node):
    def __init__(self, args: list):
        self.args = args

    def __repr__(self):
        return f'ArgListNode("{self.args}")'


class FunctionNode(Node):
    def __init__(self, ident: str, arg_list_node: ArgListNode, expr: ExprNode):
        self.ident = ident
        self.arg_list_node = arg_list_node
        self.expr = expr

    def __repr__(self):
        return f'FunctionNode("{self.ident},{self.arg_list_node},{self.expr}")'


class FunctionCallNode(Node):
    def __init__(self, ident: str, arg_list_node: ArgListNode):
        self.ident = ident
        self.arg_list_node = arg_list_node

    def __repr__(self):
        return f'FunctionNode("{self.ident},{self.arg_list_node}")'


class TupleNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TupleNode({self.left}, {self.right})"


class FstNode(Node):
    def __init__(self, tup):
        self.tup = tup

    def __repr__(self):
        return f"FstNode({self.tup})"


class SndNode(Node):
    def __init__(self, tup):
        self.tup = tup

    def __repr__(self):
        return f"SndNode({self.tup})"

class ListNode(Node):
    def __init__(self, lst, type_):
        self.lst = lst
        self.type_ = type_

    def __repr__(self):
        return f"ListNode({", ".join((str(itm) for itm in self.lst))})"


class HeadNode(Node):
    def __init__(self, lst):
        self.lst = lst

    def __repr__(self):
        return f"HeadNode({self.lst})"


class TailNode(Node):
    def __init__(self, lst):
        self.lst = lst

    def __repr__(self):
        return f"TailNode({self.lst})"


class LengthNode(Node):
    def __init__(self, lst):
        self.lst = lst

    def __repr__(self):
        return f"LengthNode({self.lst})"


# class IntTypeNode(TypeNode):
#     def __init__(self, ident: str, width: int):
#         self.ident = ident
#         self.width = width

#     def __repr__(self):
#         return f'IntTypeNode("{self.ident},{self.width}")'
