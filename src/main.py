from _pytest._code.code import E
import lark
import node
from inference import Inferencer
from dicetypes import BoolType, IntType

# See https://lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
grammar = """
start :  expr                           -> expr

expr  :  "(" expr ")"                   -> paren
      |  "true"                         -> true
      |  "false"                        -> false
      |  "flip" NUMBER                  -> flip
      |  "discrete" "(" nums ")"        -> discrete
      |  "int" "(" INT "," INT ")"      -> int_
      |  "!" expr                       -> not_     // FIXME: give ! higher
      |  "let" IDENT "=" expr "in" expr -> assign   //  precedence than & or |
      |  IDENT                          -> ident
      |  expr AND expr                  -> and_
      |  expr OR expr                   -> or_
      |  expr ADD expr                  -> add
      |  expr SUB expr                  -> sub
      |  expr MUL expr                  -> mul
      |  expr DIV expr                  -> div
      |  "if" expr "then" expr "else" expr  -> if_

nums  :  NUMBER                         -> nums_single
      |  NUMBER "," nums                -> nums_recurse

// Terminals
%import common.NUMBER
%import common.INT
IDENT :  /[a-zA-Z_][a-zA-Z0-9_]*/
AND.4 :  "&"
OR.3  :  "|"
ADD.1 :  "+"
SUB.1 :  "-"
MUL.2 :  "*"
DIV.2 :  "/"

%import common.WS
%ignore WS
"""


# The purpose of a transformer is to convert the tree outputted by Lark into
# a tree of our own format. Each method of this class corresponds to one of
# the rules (specified by the `->` in the grammar). These methods take in
# a `lark.Tree` node and replace it with the return value.
class TreeTransformer(lark.Transformer):
    def expr(self, x):  # NOTE: x is a list of terminals & nonterminals in the
        return x[0]  #       rule, not including tokens specified by double
        #       quotes in the grammar

    def paren(self, x):
        return x[0]

    def ident(self, x):
        return node.IdentNode(x[0])

    def true(self, _):
        return BoolType(True)

    def false(self, _):
        return BoolType(False)

    def flip(self, x):
        return node.FlipNode(x[0])

    def discrete(self, x):
        return node.DiscreteNode(x[0])

    def int_(self, x):
        return IntType(x[0], x[1])

    def not_(self, x):
        return node.NotNode(x[0])

    def and_(self, x):
        return node.AndNode(x[0], x[2])

    def or_(self, x):
        return node.OrNode(x[0], x[2])

    def add(self, x):
        return node.AddNode(x[0], x[2])

    def sub(self, x):
        return node.SubNode(x[0], x[2])

    def mul(self, x):
        return node.MulNode(x[0], x[2])

    def div(self, x):
        return node.DivNode(x[0], x[2])

    def assign(self, x):
        return node.AssignNode(x[0], x[1], x[2])

    def if_(self, x):
        return node.IfNode(x[0], x[1], x[2])

    def nums_single(self, x):
        return [x[0]]

    def nums_recurse(self, x):
        return [x[0]] + x[1]

    def IDENT(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token)

    def INT(self, token):
        return int(token)


def parse_string(text: str, parser: lark.Lark) -> dict:
    ast = parser.parse(text)
    ir = TreeTransformer().transform(ast)
    inferencer = Inferencer(ir, num_iterations=100000)
    return inferencer.infer()
