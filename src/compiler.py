# Contains code to do BDD compilation on our parsed tree
import node
from dicetypes import DiceType, BoolType, IntType
from bdd import BDDTree
import random


# Only does compiler for the particular tree
class TreeCompiler:
    def __init__(self, tree, variables=None):
        self.tree = tree
        self.variables = variables

    def infer(self) -> dict[DiceType, float]:
        res = self.recurseTree(self.tree)
        return res.calculate_probability()

    def recurseTree(self, treeNode) -> DiceType | None:
        if type(treeNode) is BoolType:
            if treeNode.val == True:
                return BDDTree(1.0)
            else:
                return BDDTree(0.0)

        elif type(treeNode) is node.FlipNode:
            return BDDTree(treeNode.prob)

        elif type(treeNode) is node.AndNode:
            lhs = self.recurseTree(treeNode.left)
            rhs = self.recurseTree(treeNode.right)
            lhs.replace_abs_true_node(rhs.root)
            rhs.replace_abs_false_node(lhs.abs_false_node)
            lhs.abs_true_node = rhs.abs_true_node

            return lhs

        elif type(treeNode) is node.OrNode:
            lhs = self.recurseTree(treeNode.left)
            rhs = self.recurseTree(treeNode.right)
            lhs.replace_abs_false_node(rhs.root)
            rhs.replace_abs_true_node(lhs.abs_true_node)
            lhs.abs_false_node = rhs.abs_false_node
            return lhs


        elif type(treeNode) is node.IfNode:
            cond = self.recurseTree(treeNode.cond)
            true_expr = self.recurseTree(treeNode.true_expr)
            false_expr = self.recurseTree(treeNode.false_expr)
            true_node = cond.abs_true_node
            false_node = cond.abs_false_node
            cond.replace_abs_false_node(false_expr.root)
            cond.replace_abs_true_node(true_expr.root)
            false_expr.replace_abs_false_node(false_node)
            false_expr.replace_abs_true_node(true_node)
            true_expr.replace_abs_false_node(false_node)
            true_expr.replace_abs_true_node(true_node)
            return cond

        else:
            raise NotImplementedError
