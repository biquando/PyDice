from pathlib import Path
import lark

import node
from inference import Inferencer
from compiler import PyEdaCompiler
from dicetypes import BoolType, IntType, TupleType, ListType, DiceType
import custom_distribution

for dist_class_name, dist_module_name in zip(
    custom_distribution.distribution_class_names,
    custom_distribution.distribution_module_names,
):
    exec(f"from distributions.{dist_module_name} import {dist_class_name}")

# See https://lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
grammar = f"""
?start: program_expr

?program_expr: (function_expr)* expr -> program

?function_expr: "fun" IDENT "(" [arg_list_expr] ")" "{{" expr "}}" -> function

?arg_list_expr: arg_expr ("," arg_expr)* -> arg_list

?arg_expr: IDENT ":" type -> arg

?type: "bool"                           -> bool_type
     | "(" type "," type ")"            -> tuple_type
     | "int" "(" INT ")"                 -> int_type
     | "[]" type                      -> list_type
     //| IDENT                           -> custom_type  // optional: for named types or type variables

// We add precedence to the expression groups: 
//      Arithmetic Expressions: MUL/DIV > ADD/SUB > LT,LTE,GT,GTE 
//      Logical Expressions: NOT > XOR > AND > OR > IMPLIES > IFF
// Then the precendence in general is:
//      ARITHMETIC > LOGICAL > EQUALS/NOT_EQUALS
// Since arithmetic and logical operators don't mix, having them in the same precedence is fine

?expr: equality_expr
         | "fst" expr                -> fst
         | "snd" expr                -> snd
         | "head" expr               -> head
         | "tail" expr               -> tail
         | "length" expr             -> length

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
     | "(" expr "," expr ")"                -> tuple_expr
     | "[" expr ("," expr)* "]"             -> list_expr
     | "true"                               -> true
     | "false"                              -> false
     | "flip" NUMBER                        -> flip
     | custom                               -> custom
     | "int" "(" INT "," INT ")"            -> int_
     | "let" IDENT ASSIGN expr "in" expr    -> assign
     | "if" expr "then" expr "else" expr    -> if_
     | IDENT                                -> ident
     | function_call_expr
     | "observe" expr                       -> observe
    
?function_call_expr: IDENT "(" [arg_exprs] ")" -> function_call

?arg_exprs: expr ("," expr)* -> arg_list

{custom_distribution.grammar}

nums  :  NUMBER                         -> nums_single
      |  NUMBER "," nums                -> nums_recurse

ints  : INT                             -> ints_single
      | INT "," ints                    -> ints_recurse

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

    def custom(self, x):
        return x[0]

    # This dynamically creates a new method for each custom distribution
    for dist_class, dist_class_name in zip(
        custom_distribution.distribution_classes,
        custom_distribution.distribution_class_names,
    ):
        exec(
            f"def custom_{dist_class.NAME}(self, x): " + f"return {dist_class_name}(*x)"
        )

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

    def tuple_expr(self, x):
        return node.TupleNode(x[0], x[1])

    def list_expr(self, x):
        return node.ListNode(x, DiceType)

    def implies(self, x):
        return node.OrNode(node.NotNode(x[0]), x[2])

    def iff(self, x):
        return node.AndNode(self.implies(x), self.implies(x[::-1]))

    def eq(self, x):
        return node.EqualNode(x[0], x[2])

    def neq(self, x):
        return node.NotNode(self.eq(x))

    def lt(self, x):
        return node.LessThanNode(x[0], x[2])

    def lte(self, x):
        return node.OrNode(self.lt(x), self.eq(x))

    def gt(self, x):
        return node.NotNode(self.lte(x))

    def gte(self, x):
        return node.NotNode(self.lt(x))

    def xor(self, x):
        return node.AndNode(self.or_(x), node.NotNode(self.and_(x)))

    def assign(self, x):
        return node.AssignNode(x[0], x[2], x[3])

    def if_(self, x):
        return node.IfNode(x[0], x[1], x[2])

    def nums_single(self, x):
        return [x[0]]

    def nums_recurse(self, x):
        return [x[0]] + x[1]

    def ints_single(self, x):
        return [x[0]]

    def ints_recurse(self, x):
        return [x[0]] + x[1]

    def IDENT(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token)

    def INT(self, token):
        return int(token)

    def program(self, x):
        return node.ProgramNode(x)

    def bool_type(self, token):
        return BoolType(True)

    def int_type(self, x):
        return IntType(x[0], 0)

    def tuple_type(self, x):
        return TupleType(x[0], x[1])

    def list_type(self, x):
        return ListType([], x[0])

    def fst(self, x):
        return node.FstNode(x[0])

    def snd(self, x):
        return node.SndNode(x[0])

    def head(self, x):
        return node.HeadNode(x[0])

    def tail(self, x):
        return node.TailNode(x[0])

    def length(self, x):
        return node.LengthNode(x[0])

    def arg(self, x):
        return node.ArgNode(x[0], x[1])

    def arg_list(self, x):
        args = []
        for arg in x:
            args.append(arg)
        return node.ArgListNode(args)

    def function(self, x):
        if x[1]:
            return node.FunctionNode(x[0], x[1], x[2])
        else:
            return node.FunctionNode(x[0], node.ArgListNode([]), x[2])

    def function_call(self, x):
        if x[1]:
            return node.FunctionCallNode(x[0], x[1])
        else:
            return node.FunctionCallNode(x[0], node.ArgListNode([]))

    def observe(self, x):
        return node.ObserveNode(x[0])


def parse_string(text: str, parser: lark.Lark) -> dict:
    ast = parser.parse(text)
    ir = TreeTransformer().transform(ast)
    inferencer = Inferencer(ir, num_iterations=100000)
    return inferencer.infer()


def execute_from_file(
    p: Path, parser: lark.Lark = lark.Lark(grammar, parser="lalr")
) -> dict:
    with open(p, "r") as f:
        s = f.read()

    return parse_string(s, parser)


def parse_string_compile(text: str, parser: lark.Lark) -> dict:
    ast = parser.parse(text)
    ir = TreeTransformer().transform(ast)
    compiled_tree = PyEdaCompiler(ir)
    return compiled_tree.infer()
