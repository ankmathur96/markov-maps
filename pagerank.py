from __future__ import division
import networkx as graphs
import numpy as np

def assign_distribution(neighbors, g_map):
	if len(neighbors) == 0:
		return []
	neighbors_total = sum([neighbor.score for neighbor in neighbors])
	return [neighbor / neighbors_total for neighbor in range(len(neighbors))]

def get_node_index(node):
	return node.id

def create_pr_matrix(g_map):
	pr = np.zeros((len(g_map), len(g_map)))
	for node in g_map.nodes_iter():
		neighbors = g_map.neighbors(node)
		distribution = assign_distribution(neighbors, g_map)
		for i, n in enumerate(neighbors):
			pr[get_node_index(node)][get_node_index(n)] = distribution[i]
	return pr

def alter_graph(g_map):
	reversed_graph = g_map.reverse(copy=True)

def test_pr_matrix():
	N_NODES = 5
	g = graphs.MultiGraph()
	for i in range(N_NODES):
		g.add_node(i)
		g.add_edge(i,i)
	for i in range(N_NODES):
		g.add_edge(i, i+1 % N_NODES)
	print(create_pr_matrix(g))

if __name__ == "__main__":
	print(test_pr_matrix())
