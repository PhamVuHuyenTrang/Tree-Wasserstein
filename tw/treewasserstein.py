from typing import List, Tuple, Optional
from queue import Queue

EdgeList = List[Tuple[int, int, float]]
Tree = List[List[Tuple[int, float, int]]]
Prob = List[float]

def isTree(num_node: int, edges: EdgeList, root_idx: int) -> bool:
    if len(edges) != num_node - 1:
        return False
    tree = [[] for _ in range(num_node)]
    visited_node = [False] * num_node
    visited_edge = [False] * len(edges)
    
    for i in range(len(edges)):
        from_, to, weight = edges[i]
        tree[from_].append((to, weight, i))
        tree[to].append((from_, weight, i))
    
    edges.clear()
    que = Queue()
    que.put(root_idx)
    visited_node[root_idx] = True
    while not que.empty():
        from_ = que.get()
        for e in tree[from_]:
            to, weight, edge_idx = e
            if visited_edge[edge_idx]:
                continue
            if visited_node[to]:
                return False
            visited_node[to] = True
            visited_edge[edge_idx] = True
            que.put(to)
            edges.append((from_, to, weight))
    
    return True

def sign(x: float) -> int:
    return 1 if x >= 0 else -1

class Node:
    def __init__(self, idx: int, is_root: bool):
        self.idx = idx
        self.is_root = is_root
        self.parent_idx = None
        self.parent_weight = None
        self.first_prob = None
        self.second_prob = None
        self.cumul_first_prob = 0
        self.cumul_second_prob = 0
        self.cumul_edge_weight = 0
        self.child_list = []

class TreeMetric:
    def __init__(self, num_node: int, edges: EdgeList, root_idx: int = 0):
        self.num_node = num_node
        self.root_idx = root_idx
        self.nodes = [Node(i, i == root_idx) for i in range(num_node)]
        
        if not isTree(num_node, edges, root_idx):
            raise ValueError("Not tree")
        
        for e in edges:
            parent, child, weight = e
            self.nodes[parent].child_list.append(child)
            self.nodes[child].parent_idx = parent
            self.nodes[child].parent_weight = weight
        
        self.leaves = [n.idx for n in self.nodes if not n.child_list]
        self.root_idx = next((n.idx for n in self.nodes if not n.parent_idx), root_idx)
    
    def accumulateNodeProb(self):
        visited_count = [0] * self.num_node
        que = Queue()
        for l in self.leaves:
            que.put(l)
        while not que.empty():
            node = self.nodes[que.get()]
            if node.is_root:
                visited_count[self.root_idx] += 1
                continue
            parent = self.nodes[node.parent_idx]
            parent.cumul_first_prob += node.cumul_first_prob
            parent.cumul_second_prob += node.cumul_second_prob
            visited_count[parent.idx] += 1
            if visited_count[parent.idx] == len(parent.child_list):
                que.put(parent.idx)
    
    def accumulateEdgeWeight(self):
        que = Queue()
        que.put(self.root_idx)
        while not que.empty():
            node = self.nodes[que.get()]
            for c in node.child_list:
                child = self.nodes[c]
                prob_diff = child.cumul_first_prob - child.cumul_second_prob
                child.cumul_edge_weight = node.cumul_edge_weight + sign(prob_diff) * child.parent_weight
                que.put(c)
    
    def setProb(self, first_prob: Prob, second_prob: Prob):
        for idx in range(self.num_node):
            self.nodes[idx].first_prob = first_prob[idx]
            self.nodes[idx].second_prob = second_prob[idx]
            self.nodes[idx].cumul_first_prob = first_prob[idx]
            self.nodes[idx].cumul_second_prob = second_prob[idx]
        self.accumulateNodeProb()
        self.accumulateEdgeWeight()
    
    def TWDistance(self, first_prob: Prob, second_prob: Prob) -> float:
        self.setProb(first_prob, second_prob)
        twd = 0
        for n in self.nodes:
            twd += n.cumul_edge_weight * (n.first_prob - n.second_prob)
        return twd

def distance(first_prob: Prob, second_prob: Prob, edges: EdgeList) -> float:
    num_node = len(first_prob)
    tm = TreeMetric(num_node, edges)
    return tm.TWDistance(first_prob, second_prob)


