# Contains code to do MonteCarlo Inferencing on our parsed tree
import node
from dicetypes import DiceType, BoolType, IntType
import random


# Only does MC for the particular tree
class TreeInferencer:
    def __init__(self, tree, variables):
        self.tree = tree
        self.variables = variables

    def infer(self) -> DiceType:
        res = self.recurseTree(self.tree)
        assert res is not None
        return res

    def recurseTree(self, treeNode) -> DiceType | None:
        if type(treeNode) is BoolType:
            return treeNode

        if type(treeNode) is IntType:
            return treeNode

        elif type(treeNode) is node.FlipNode:
            return BoolType(random.random() < treeNode.prob)

        elif type(treeNode) is node.IdentNode:
            if treeNode.ident not in self.variables:
                raise Exception("Identifier not defined:", treeNode.ident)
            return self.variables[treeNode.ident]

        elif isinstance(treeNode, node.UnaryNode):
            return treeNode.op(self.recurseTree(treeNode.operand))

        elif isinstance(treeNode, node.BinaryNode):
            return treeNode.op(
                self.recurseTree(treeNode.left), self.recurseTree(treeNode.right)
            )

        elif isinstance(treeNode, node.AssignNode):
            self.variables[treeNode.ident] = self.recurseTree(treeNode.val)
            return self.recurseTree(treeNode.rest)

        else:
            raise Exception("Tree Node Unknown:", treeNode)


# Should do numerous runs of inference + handle functions
class Inferencer:
    # TODO - Add function support once it's implemented
    def __init__(self, tree, variables=None, num_iterations=1000):
        self.tree = tree
        self.variables = variables if variables is not None else {}
        self.treeInferencer = TreeInferencer(tree, self.variables)
        self.num_its = num_iterations

    def infer(self) -> dict[DiceType, float]:
        results = {}
        for _ in range(self.num_its):
            res = self.treeInferencer.infer()
            if res not in results:
                results[res] = 1
            else:
                results[res] += 1

        for outcome in results:
            results[outcome] /= self.num_its
        return results
