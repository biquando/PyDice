import lark
import node
from inference import Inferencer

# See https://lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
grammar = '''
start :  expr                           -> expr

expr  :  "(" expr ")"                   -> paren
      |  "true"                         -> true
      |  "false"                        -> false
      |  "flip" "(" NUMBER ")"          -> flip
      |  "!" expr                       -> not_     // FIXME: give ! higher
      |  IDENT                          -> ident    //  precedence than & or |
      |  expr AND expr                  -> and_
      |  expr OR expr                   -> or_


// Terminals
%import common.NUMBER
IDENT :  /[a-zA-Z_][a-zA-Z0-9_]*/
AND.2 :  "&"
OR.1  :  "|"

%import common.WS
%ignore WS
'''

# The purpose of a transformer is to convert the tree outputted by Lark into
# a tree of our own format. Each method of this class corresponds to one of
# the rules (specified by the `->` in the grammar). These methods take in
# a `lark.Tree` node and replace it with the return value.
class TreeTransformer(lark.Transformer):
    def expr(self, x):   # NOTE: x is a list of terminals & nonterminals in the
        return x[0]      #       rule, not including tokens specified by double
    def paren(self, x):  #       quotes in the grammar
        return x[0]
    def ident(self, x):
        return node.IdentNode(x[0])
    def true(self, _):
        return True
    def false(self, _):
        return False
    def flip(self, x):
        return node.FlipNode(x[0])
    def not_(self, x):
        return node.NotNode(x[0])
    def and_(self, x):
        return node.AndNode(x[0], x[2])
    def or_(self, x):
        return node.OrNode(x[0], x[2])
    def IDENT(self, token):
        return str(token)
    def NUMBER(self, token):
        return float(token)


def main():
    INPUT = '(true | flip(0.25)) & !xyz'
    l = lark.Lark(grammar, parser='lalr')
    tree = l.parse(INPUT)
    new_tree = TreeTransformer().transform(tree)

    print('INPUT:', INPUT)
    print(new_tree)

    # Tree Inferencer Test
    inferencer = Inferencer( new_tree, {"xyz":True} )
    print( "Result after 1000 iterations:", inferencer.infer() )

    # Another example
    example1 = 'flip(0.33) | flip(0.25)'
    print( "Example:", example1 )
    tree2 = l.parse( example1 )
    new_tree2 = TreeTransformer().transform(tree2)
    inferencer2 = Inferencer( new_tree2, num_iterations = 10000 )
    print( "Result after 10000 iterations (Should be around 0.5):", inferencer2.infer() )

    #print( new_tree.op()(1,1) )


if __name__ == '__main__':
    main()
