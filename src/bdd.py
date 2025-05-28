from dicetypes import DiceType, BoolType

class BDDNode:
    # rolling id (static variable)
    current_node_id = 0
    def __init__(self, weight: float, true_node: 'BDDNode' = None, false_node: 'BDDNode'  = None):
        self.parents = []
        self.true_node = None
        self.false_node = None
        self.node_id = BDDNode.current_node_id
        self.add_true_node(true_node)
        self.add_false_node(false_node)
        self.weight = weight
        BDDNode.current_node_id += 1
    def remove_true_node(self):
        if self.true_node != None:
            self.true_node.parents.remove(self)
            self.true_node = None
    def remove_false_node(self):
        if self.false_node != None:
            self.false_node.parents.remove(self)
            self.false_node = None
    # this replaces any true node already present
    def add_true_node(self, true_node: 'BDDNode'):
        self.remove_true_node()
        self.true_node = true_node
        if true_node != None:
            true_node.parents.append(self)
    # this replaces any false node already present
    def add_false_node(self, false_node: 'BDDNode'):
        self.remove_false_node()
        self.false_node = false_node
        if false_node != None:
            print("add false node", self.node_id, self.false_node.node_id)
            false_node.parents.append(self)


# represents an absolute leaf node
class LeafNode(BDDNode):
    def __init__(self, is_true_node: bool):
        super().__init__(0.0)
        self.is_true_node = is_true_node

class BDDTree:
    def __init__(self, weight):
        self.abs_true_node = LeafNode(True)
        self.abs_false_node = LeafNode(False)
        self.root = BDDNode(weight, self.abs_true_node, self.abs_false_node)
    def replace_abs_true_node(self, new_node: BDDNode):
        copy = self.abs_true_node.parents.copy()
        for parent in copy:
            if parent.true_node == self.abs_true_node:
                parent.add_true_node(new_node)
            elif parent.false_node == self.abs_true_node:
                parent.add_false_node(new_node)

    
    def replace_abs_false_node(self, new_node: BDDNode):
        copy = self.abs_false_node.parents.copy()
        for parent in copy:
            if parent.true_node == self.abs_false_node:
                parent.add_true_node(new_node)
            elif parent.false_node == self.abs_false_node:
                parent.add_false_node(new_node)
            
    def calculate_probability_node(self, node: BDDNode) -> float:
        if node == self.root:
            return 1.0

        val = 0.0
        for parent in node.parents:
            prob = self.calculate_probability_node(parent)
            if node == parent.true_node:
                val += parent.weight * prob
            else:
                val += (1.0 - parent.weight) * prob
            print(val, node.node_id, prob)
        return val

    def calculate_probability(self) -> dict[DiceType, float]:
        self.debug_print(self.root)
        print(self.abs_true_node.node_id, "truth")
        return {BoolType(True): self.calculate_probability_node(self.abs_true_node),
                BoolType(False): self.calculate_probability_node(self.abs_false_node)}

    def debug_print(self, node: BDDNode):
        if node is not None:
            if node.true_node is not None:
                print(f'node: {node.node_id} {node.weight} true node: {node.true_node.node_id}')
                self.debug_print(node.true_node)
            if node.false_node is not None:
                print(f'node: {node.node_id} {node.weight} false node: {node.false_node.node_id}')
                self.debug_print(node.false_node)

