import log

class Node:
    ...

class ExprNode(Node):
    ...

class IdentNode(ExprNode):
    def __init__(self, ident: str):
        self.ident = ident
    def __repr__(self):
        return f'IdentNode("{self.ident}")'

class FlipNode(ExprNode):
    def __init__(self, prob: float):
        self.prob = prob
    def __repr__(self):
        return f'FlipNode({self.prob})'

### Unary operations ###########################################################

class _UnaryNode(ExprNode):
    def __init__(self, operand: ExprNode):
        self.operand = operand
    def __repr__(self):
        return '(\n' + \
               log.indent(self.operand) + '\n' + \
               ')'

class NotNode(_UnaryNode):
    def __init__(self, operand: ExprNode):
        super().__init__(operand)
    def __repr__(self):
        return 'NotNode' + super().__repr__()

### Binary operations ##########################################################

class _BinaryNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right
    def __repr__(self):
        return '(\n' + \
               log.indent(self.left) + ',\n' + \
               log.indent(self.right) + '\n' + \
               ')'

class AndNode(_BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
    def __repr__(self):
        return 'AndNode' + super().__repr__()

class OrNode(_BinaryNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        super().__init__(left, right)
    def __repr__(self):
        return 'OrNode' + super().__repr__()
