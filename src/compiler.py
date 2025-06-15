# Contains code to do BDD compilation on our parsed tree
import node
from dicetypes import DiceType, BoolType, IntType
from pyeda.inter import *

class PyEdaCompiler:
    def __init__(self, tree):
        self.tree = tree
        self.variable_asgn = {}
        self.flip_prob = {}
        self.flip_label = 0
        self.function_to_node = {}
        self.function_to_compile = {}
        self.adjacency_list = {}
        self.function_results = {}
    
    # infer should be run on a program, with no added context
    def infer(self) -> dict[DiceType, float]:
        if type(self.tree) is not node.ProgramNode:
            raise Exception("infer() should only be run on root program nodes")
        self.precomputeFunc(self.tree, None)
        function_list = self.topoSort()
        if len(function_list) != len(self.function_to_node):
            raise Exception("recursion/mutual recursive functions detected")
        for function in function_list:
            self.compileFunc(function)
        return self.infer_tree(self.tree)

    # infer_tree carries all the extra scoping that has already been added in program
    def infer_tree(self, tree) -> dict[DiceType, float]:
        expr = self.recurseTree(tree)
        bdd = expr2bdd(expr)
        prob = 0.0
        for satisfiability in list(bdd.satisfy_all()):
            clause_prob = 1.0
            for var, val in satisfiability.items():
                var = str(var)
                if val == 0:
                    clause_prob *= 1.0 - self.flip_prob[var]
                else:
                    clause_prob *= self.flip_prob[var]
            prob += clause_prob
        return {BoolType(True): prob, BoolType(False): 1.0-prob}

    # this tracks all call sites to make sure no recursion or mutual recursion happens
    def precomputeFunc(self, treeNode, curr_func):
        if type(treeNode) is node.ProgramNode:
            for function in treeNode.functions:
                self.function_to_node[function.ident] = function
                self.function_results[function.ident] = 0
                self.adjacency_list[function.ident] = set()
            for function in treeNode.functions:
                self.precomputeFunc(function, function.ident)
        elif type(treeNode) is node.FunctionNode:
            self.precomputeFunc(treeNode.expr, curr_func)

        elif type(treeNode) is node.FunctionCallNode:
            self.adjacency_list[treeNode.ident].add(curr_func)
            arg_expr = treeNode.arg_list_node.args
            for argument in arg_expr:
                self.precomputeFunc(argument, curr_func)

        elif isinstance(treeNode, node.UnaryNode):
            self.precomputeFunc(treeNode.operand, curr_func)

        elif isinstance(treeNode, node.BinaryNode):
            self.precomputeFunc(treeNode.left, curr_func)
            self.precomputeFunc(treeNode.right, curr_func)

        elif isinstance(treeNode, node.AssignNode):
            self.precomputeFunc(treeNode.rest, curr_func)

        elif isinstance(treeNode, node.IfNode):
            self.precomputeFunc(treeNode.cond, curr_func)
            self.precomputeFunc(treeNode.true_expr, curr_func)
            self.precomputeFunc(treeNode.false_expr, curr_func)

        elif type(treeNode) is node.ObserveNode:
            self.precomputeFunc(treeNode.observation, curr_func)

    # do topo sort to deal with multiple functions
    def topoSort(self):
        indegree = {}
        for function in self.function_to_node.keys():
            indegree[function] = 0
        for function in self.function_to_node.keys():
            for next_func in self.adjacency_list[function]:
                indegree[next_func] += 1
        topo_list = []
        queue = []
        for function in indegree.keys():
            if indegree[function] == 0:
                queue.append(function)
        queue_pos = 0
        while queue_pos < len(queue):
            topo_list.append(queue[queue_pos])
            for next_func in self.adjacency_list[queue[queue_pos]]:
                if (next_func == queue[queue_pos]):
                    return []
                indegree[next_func] -= 1
                if(indegree[next_func] == 0):
                    queue.append(next_func)
            queue_pos += 1
        return topo_list

    def compileFunc(self, func):
        expr, formal_param_list = self.function_to_node[func].expr, self.function_to_node[func].arg_list_node.args
        for formal_param in formal_param_list:
            self.variable_asgn[str(formal_param.ident)] = None #dummy values and a hack - these never get filled!
        eda_expr = self.recurseTree(expr)
        compiled_bdd = expr2bdd(eda_expr)
        self.function_to_compile[func] = list(compiled_bdd.satisfy_all())
    
    def processFunc(self, treeNode) -> expr:
        ident, arg_expr_list = treeNode.ident, treeNode.arg_list_node.args
        parameter_expression = {}
        # Check if function exists
        if( ident not in self.function_to_node ):
            raise Exception("Function identifier not defined:", ident)
        formal_param_list = self.function_to_node[ident].arg_list_node.args
        formal_param_list_names = []
        for formal_param in formal_param_list:
            formal_param_list_names.append(formal_param.ident)
        if len(arg_expr_list) != len(formal_param_list):
            raise AttributeError(f"Argument Length does not match: Param len {len( formal_param_list )} != Arg len {len(arg_expr_list)}")
        for arg_expr, formal_param in zip(arg_expr_list, formal_param_list_names):
            arg_expr_compiled = self.recurseTree(arg_expr)
            parameter_expression[formal_param] = arg_expr_compiled
        list_of_clauses = []
        for satisfiability in self.function_to_compile[ident]:
            clause_expr = []
            for var, val in satisfiability.items():
                var = str(var)
                literal = None
                if var in formal_param_list_names:
                    literal = parameter_expression[var]
                else:
                    # this has to be a flip
                    probability = self.flip_prob[var]
                    # we need to reset flips so that they are independent between function calls
                    # see paper section 4.3 for more details
                    flip_var = exprvar('f', self.flip_label)
                    self.flip_prob[str(flip_var)] = probability
                    self.flip_label += 1
                    literal = flip_var
                if val == 0:
                    literal = Not(literal)
                clause_expr.append(literal)
            list_of_clauses.append(And(*clause_expr))
        return Or(*list_of_clauses)

    def recurseTree(self, treeNode)-> expr:
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
            self.flip_prob[str(flip_var)] = treeNode.prob
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
            if treeNode.ident not in self.variable_asgn:
                raise Exception("Identifier not defined:", treeNode.ident)
            if self.variable_asgn[str(treeNode.ident)] == None:
                return exprvar(treeNode.ident)
            return self.variable_asgn[str(treeNode.ident)] 

        elif type(treeNode) is node.AssignNode:
            self.variable_asgn[str(treeNode.ident)] = self.recurseTree(treeNode.val)
            return self.recurseTree(treeNode.rest)
            
        elif type(treeNode) is node.FunctionCallNode:
            return self.processFunc(treeNode)

        else:
            raise NotImplementedError
