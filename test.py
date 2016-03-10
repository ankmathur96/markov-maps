import networkx
import matplotlib.pyplot as plt
class Node():
    def __init__(self, nid, reversed_graph):
        self.id = nid
        self.reversed = reversed_graph
        self.x = None
        self.y = None
        self.score = None

    def __eq__(self, other):
        return self.id == other.id and self.reversed == other.reversed
    def __hash__(self):
    	return hash((self.id, self.reversed))
    def __str__(self):
    	return repr(self)
    def __repr__(self):
    	return 'Node(id=' + str(self.id) + ', reversed=' + str(self.reversed) + ', (x,y) = (' + str(self.x) + ',' + str(self.y) + '), score=' + str(self.score) + ')'

def find_node(nid, coords):
    for x in coords:
        if x[0] == nid:
            return x
    return -1
def convert_to_graph(coords, adjacency_list):
    graph = networkx.MultiDiGraph()
    for k in adjacency_list:
        node_coord = find_node(k, coords)
        node_to_add = Node(k, False)
        if node_coord != -1:
            node_to_add.x, node_to_add.y = node_coord[1]
        graph.add_node(node_to_add)
    for k in adjacency_list:
        graph.add_edge(Node(k, False), Node(k, False))
        for neighbor in adjacency_list[k]:
            if graph.has_edge(Node(neighbor,False), Node(k, False)):
                continue
            else:
                graph.add_edge(Node(k, False), Node(neighbor, False))
    # networkx.draw(graph)
    # plt.show()
    print graph.nodes()
    reverse_graph = graph.reverse(copy=True)
    # networkx.draw(graph)
    # plt.show()
    for node in reverse_graph.nodes_iter():
        node_to_add = Node(node.id, True)
        node_to_add.x, node_to_add.y = node.x, node.y
        graph.add_node(node_to_add)
    for node in reverse_graph.nodes_iter():
        new_node = Node(node.id, True)
        for n in reverse_graph.neighbors(node):
            graph.add_edge(new_node, Node(n.id, True))
    print graph.nodes()
    for node in reverse_graph.nodes_iter():
        graph.add_edge(Node(node.id, True), Node(node.id, False))
        graph.add_edge(Node(node.id, False), Node(node.id, True))
    print graph.nodes()
    return graph
def test_convert_to_graph():
	adjacency_list = {0 : [1,2], 1 : [2], 2 : []}
	graph = convert_to_graph([(0,(0,0)), (1,(1,1)), (2,(2,2))], adjacency_list)
	networkx.draw(graph, pos={Node(0, False) : (0,3), Node(0, True) : (0,-3), Node(1, False) : (3,4), Node(1, True) : (3, -2), Node(2, False) : (6, 3), Node(2, True) : (6, -3)})
	plt.show()
	print 'showed the graph'
test_convert_to_graph()