# Contains code to do MonteCarlo Inferencing on our parsed tree
from node import *
import random

# Only does MC for the particular tree
class TreeInferencer:
    def __init__(self, tree, variables ):
        self.tree = tree
        self.variables = variables

    def infer( self ):
        return self.recurseTree( self.tree )

    def recurseTree( self, treeNode ):
        if( type( treeNode ) == bool ):
            return treeNode
        elif( type( treeNode ) == FlipNode ):
            return random.random() < treeNode.prob
        elif( type( treeNode ) == IdentNode ):
            if( treeNode.ident not in self.variables ):
                raise Exception( "Identifier not defined:", treeNode.ident )
            return self.variables[treeNode.ident]
        elif( isinstance( treeNode, UnaryNode ) ):
            return treeNode.op( self.recurseTree( treeNode.operand ) )
        elif( isinstance( treeNode, BinaryNode ) ):
            return treeNode.op( self.recurseTree( treeNode.left ), self.recurseTree( treeNode.right ) )
        elif( isinstance( treeNode, AssignNode ) ):
            self.variables[treeNode.ident] = self.recurseTree(treeNode.val)
            return self.recurseTree(treeNode.rest)
        else:
            raise Exception( "Tree Node Unknown:", treeNode )

# Should do numerous runs of inference + handle functions
class Inferencer:
    # TODO - Add function support once it's implemented
    def __init__(self, tree, variables = {}, num_iterations = 1000 ):
        self.tree = tree
        self.variables = variables
        self.treeInferencer = TreeInferencer( tree, variables )
        self.num_its = num_iterations
    
    def infer( self ):
        true_res = 0
        for _ in range( self.num_its ):
            true_res += self.treeInferencer.infer()
        return true_res / self.num_its
