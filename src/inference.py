# Contains code to do MonteCarlo Inferencing on our parsed tree
import random
from collections import Counter

import custom_distribution
import node
from dicetypes import DiceType, BoolType, IntType


# Only does MC for the particular tree
class TreeInferencer:
    def __init__(self, tree, variables, seed=None, functions = {}):
        self.tree = tree
        self.variables = variables
        self.functions = functions # Could be cool for recursion?
        self.rng = random.Random()
        self.rng.seed(seed)

    def infer(self) -> DiceType:
        res = self.recurseTree(self.tree)
        assert res is not None
        return res

    def registerFunction( self, function: node.FunctionNode ):
        ident, arg_list, expr = function.ident, function.arg_list_node.args, function.expr
        self.functions[ident] = [arg_list, expr]

    def processFunction( self, function: node.FunctionCallNode):
        ident, arg_expr_list = function.ident, function.arg_list_node.args

        # Check if function exists
        if( ident not in self.functions ):
            raise Exception("Function identifier not defined:", ident)

        # Check if length of arguments the same
        param_list, function_expr = self.functions[ident]
        if( len( param_list ) != len( arg_expr_list ) ):
            raise AttributeError(f"Argument Length does not match: Param len {len( param_list )} != Arg len {len(arg_expr_list)}")

        # Process expressions in arg_list
        arguments = []
        for expr in arg_expr_list:
            arguments.append( self.recurseTree( expr ) )

        # Check if arguments all sound
        var_map = {}
        for i in range( len( arguments ) ):
            param_ident, param_type = param_list[i].ident, param_list[i].type
            arguments[i].verify_types( param_type )
            var_map[param_ident] = arguments[i]

        # Call function
        # Can allow recursion by passing in existing functions.
        function_tf = TreeInferencer( function_expr, var_map, functions = self.functions )

        return function_tf.infer()

    def recurseTree(self, treeNode) -> DiceType | None:
        if type(treeNode) is BoolType:
            return treeNode

        if type(treeNode) is IntType:
            return treeNode

        elif type(treeNode) is node.ProgramNode:
            for function in treeNode.functions:
                self.registerFunction( function )

            return self.recurseTree( treeNode.expr )

        elif type(treeNode) is node.FunctionCallNode:
            return self.processFunction( treeNode )

        elif type(treeNode) is node.FlipNode:
            return BoolType(self.rng.random() < treeNode.prob)

        elif isinstance(treeNode, custom_distribution.CustomDistribution):
            return treeNode.sample()

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

        elif isinstance(treeNode, node.IfNode):
            cond = self.recurseTree(treeNode.cond)
            if type(cond) is not BoolType:
                raise TypeError("Condition must be BoolType")
            if cond.val:
                return self.recurseTree(treeNode.true_expr)
            else:
                return self.recurseTree(treeNode.false_expr)

        else:
            raise Exception("Tree Node Unknown:", treeNode)


# Should do numerous runs of inference + handle functions
class Inferencer:
    # TODO - Add function support once it's implemented
    def __init__(self, tree, variables=None, num_iterations=1000, seed=None):
        self.tree = tree
        self.variables = variables if variables is not None else {}
        self.treeInferencer = TreeInferencer(tree, self.variables, seed)
        self.num_its = num_iterations

    def infer(self) -> dict[DiceType, float]:
        results = Counter()
        for _ in range(self.num_its):
            res = self.treeInferencer.infer()
            results[res] += 1

        return {outcome: count / self.num_its for outcome, count in results.items()}
