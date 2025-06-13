# Contains code to do BDD compilation on our parsed tree
import node
from dicetypes import DiceType, BoolType, IntType
from pyeda.inter import *

class PyEdaCompiler:
    def __init__(self, tree):
        self.tree = tree
        self.variable_prob = {}
        self.flip_label = 0

    def infer(self) -> dict[DiceType, float]:
        expr = self.recurseTree(self.tree)
        bdd = expr2bdd(expr)
        prob = 0.0
        print(expr)
        for satisfiability in list(bdd.satisfy_all()):
            clause_prob = 1.0
            for var, val in satisfiability.items():
                var = str(var)
                if val == 0:
                    clause_prob *= 1.0 - self.variable_prob[var]
                else:
                    clause_prob *= self.variable_prob[var]
            prob += clause_prob
        return {BoolType(True): prob, BoolType(False): 1.0-prob}

    def recurseTree(self, treeNode)-> expr:
        print(type(treeNode))
        if type(treeNode) is node.ProgramNode:
            # no support for functions at this time
            return self.recurseTree( treeNode.expr )
        elif type(treeNode) is BoolType:
            if treeNode.val == True:
                return expr(1)
            else:
                return expr(0)

        elif type(treeNode) is node.FlipNode:
            flip_var = exprvar('f', self.flip_label)
            self.variable_prob[str(flip_var)] = treeNode.prob
            self.flip_label += 1
            return flip_var

        elif type(treeNode) is node.AndNode:
            lhs = self.recurseTree(treeNode.left)
            rhs = self.recurseTree(treeNode.right)
            return expr(And(lhs, rhs))

        elif type(treeNode) is node.OrNode:
            lhs = self.recurseTree(treeNode.left)
            rhs = self.recurseTree(treeNode.right)
            return expr(Or(lhs, rhs))
        
        elif type(treeNode) is node.NotNode:
            operand = self.recurseTree(treeNode.operand)
            return expr(Not(operand))

        elif type(treeNode) is node.IfNode:
            cond = self.recurseTree(treeNode.cond)
            true_expr = self.recurseTree(treeNode.true_expr)
            false_expr = self.recurseTree(treeNode.false_expr)
            return expr(Or(And(cond, true_expr), And(Not(cond), false_expr)))
        
        elif type(treeNode) is node.IfNode:
            cond = self.recurseTree(treeNode.cond)
            true_expr = self.recurseTree(treeNode.true_expr)
            false_expr = self.recurseTree(treeNode.false_expr)
            return expr(Or(And(cond, true_expr), And(Not(cond), false_expr)))
        
        elif type(treeNode) is node.IdentNode:
            if treeNode.ident not in self.variable_prob:
                raise Exception("Identifier not defined:", treeNode.ident)
            return exprvar(treeNode.ident)

        elif type(treeNode) is node.AssignNode:
            compiled_tree = PyEdaCompiler(treeNode.val)
            compiled_tree_val = compiled_tree.infer()[BoolType(True)]
            self.variable_prob[treeNode.ident] = compiled_tree_val
            return self.recurseTree(treeNode.rest)

        else:
            raise NotImplementedError
