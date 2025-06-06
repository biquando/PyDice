from pathlib import Path
import lark

import node
from inference import Inferencer
from dicetypes import BoolType, IntType

# See https://lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
grammar = """
?start: expr

// We add precedence to the expression groups: 
//      Arithmetic Expressions: MUL/DIV > ADD/SUB > LT,LTE,GT,GTE 
//      Logical Expressions: NOT > XOR > AND > OR > IMPLIES > IFF
// Then the precendence in general is:
//      ARITHMETIC > LOGICAL > EQUALS/NOT_EQUALS
// Since arithmetic and logical operators don't mix, having them in the same precedence is fine

?expr: equality_expr     

?equality_expr: iff_expr
         | equality_expr EQUALS iff_expr      -> eq
         | equality_expr NOT_EQUALS iff_expr  -> neq

?iff_expr: implies_expr
         | implies_expr IFF iff_expr -> iff

?implies_expr: or_expr
         | or_expr IMPLIES implies_expr -> implies

?or_expr: and_expr
        | or_expr OR and_expr       -> or_

?and_expr: xor_expr
         | and_expr AND xor_expr  -> and_

?xor_expr: unary_expr
         | unary_expr XOR xor_expr  -> xor

?unary_expr: NOT unary_expr         -> not_
           | compare_expr

?compare_expr: add_expr
        | compare_expr LESS_THAN add_expr               -> lt
        | compare_expr LESS_THAN_OR_EQUALS add_expr      -> lte
        | compare_expr GREATER_THAN add_expr            -> gt
        | compare_expr GREATER_THAN_OR_EQUALS add_expr   -> gte

?add_expr: mul_expr
         | add_expr ADD mul_expr   -> add
         | add_expr SUB mul_expr   -> sub

?mul_expr: atom
         | mul_expr MUL atom     -> mul
         | mul_expr DIV atom     -> div

?atom: "(" expr ")"
     | "true"                               -> true
     | "false"                              -> false
     | "flip" NUMBER                        -> flip
     | "discrete" "(" nums ")"              -> discrete
     | "int" "(" INT "," INT ")"            -> int_
     | "let" IDENT ASSIGN expr "in" expr    -> assign
     | "if" expr "then" expr "else" expr    -> if_
     | IDENT                                -> ident

nums  :  NUMBER                         -> nums_single
      |  NUMBER "," nums                -> nums_recurse

// Terminals
%import common.NUMBER
%import common.INT
IDENT :  /[a-zA-Z_][a-zA-Z0-9_]*/
NOT : "!"
AND :  "&&"
OR  :  "||"
IMPLIES.2 : "->"
IFF: "<->"
EQUALS: "=="
ASSIGN: "="
NOT_EQUALS: "!="
LESS_THAN: "<"
LESS_THAN_OR_EQUALS: "<="
GREATER_THAN: ">"
GREATER_THAN_OR_EQUALS: ">="
XOR: "^"
ADD :  "+"
SUB :  "-"
MUL :  "*"
DIV :  "/"

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
        return node.NotNode(x[1])

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

    def implies(self, x):
        return node.OrNode(node.NotNode(x[0]), x[2])

    def iff(self, x):
        return node.AndNode( self.implies( x ), self.implies( x[::-1] ) )
    
    def eq(self, x):
        return node.EqualNode( x[0], x[2] )

    def neq(self,x):
        return node.NotNode( self.eq( x ) )
    
    def lt(self,x):
        return node.LessThanNode( x[0], x[2] )
    
    def lte(self,x):
        return node.OrNode( self.lt(x), self.eq(x) )
    
    def gt(self,x):
        return node.NotNode( self.lte(x) )

    def gte(self,x):
        return node.NotNode( self.lt(x) )

    def xor(self,x):
        return node.AndNode( self.or_(x), node.NotNode( self.and_(x) ) )

    def assign(self, x):
        return node.AssignNode(x[0], x[2], x[3])

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
    print( ir )
    inferencer = Inferencer(ir, num_iterations=100000)
    return inferencer.infer()


def execute_from_file(
    p: Path, parser: lark.Lark = lark.Lark(grammar, parser="lalr")
) -> dict:
    with open(p, "r") as f:
        s = f.read()

    return parse_string(s, parser)
