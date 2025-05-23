# Contains code to do MonteCarlo Inferencing on our parsed tree
import node
import random


# Only does MC for the particular tree
class TreeInferencer:
    def __init__(self, tree, variables):
        self.tree = tree
        self.variables = variables

    def infer(self):
        return self.recurseTree(self.tree)

    def recurseTree(self, treeNode):
        if type(treeNode) is bool:
            return treeNode
        elif type(treeNode) is node.FlipNode:
            return random.random() < treeNode.prob
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

    def infer(self):
        true_res = 0
        for _ in range(self.num_its):
            true_res += 1 if self.treeInferencer.infer() else 0
        return true_res / self.num_its
