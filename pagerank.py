from __future__ import division
import networkx as graphs
import numpy as np
import random
import math


#graph is a networkx graph
#node is networkx node
#returns a dictionary of {neighbor: node to neighbor transition prob}
def get_node_to_neighbors_prob(graph, neighbors):
    trans_prob_dict = []
    if len(neighbors) == 1:
        return [1]
    sum_hwy_score = 0
    neighbor_scores = []
    for neighbor in neighbors:
        neighbor_scores.append(neighbor.score)
        sum_hwy_score += 1 / (0.001 + neighbor.factors['hwy_dist'])
    sum_neighbor_score = sum(neighbor_scores)
    # avg_neighbor_score = sum_neighbor_score / len(neighbor_scores)
    # neighbor_scores = [x - avg_neighbor_score for x in neighbor_scores]
    # min_score = 4 * abs(min(neighbor_scores))
    # neighbor_scores = [x + min_score for x in neighbor_scores]
    # sum_neighbor_score = sum(neighbor_scores)
    for i, neighbor in enumerate(neighbors):
        trans_prob_dict.append(0.7 * (neighbor_scores[i] / sum_neighbor_score) + 0.3 * (1 / (0.001 + neighbor.factors['hwy_dist']) / sum_hwy_score))
    return trans_prob_dict

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

def crawl(graph, node_mapping, num_of_visits, restart_prob=0.01):
    nodes = graph.nodes()
    curr = random.choice(nodes)
    encountered = [0 for i in xrange(len(node_mapping))]
    for i in xrange(num_of_visits):
        encountered[curr.id] += 1
        if random.random() < 0.3 * (1 - curr.factors['capacity']):
            continue
        if random.random() > restart_prob:
            neighbors = graph.neighbors(curr)
            if len(neighbors) == 0:
                curr = random.choice(nodes)
                continue
            dist = get_node_to_neighbors_prob(graph, neighbors)
            r = random.random()
            j = 0
            while r > dist[j]:
                r -= dist[j]
                j += 1
            curr = neighbors[j]
        else:
            curr = random.choice(nodes)
    encountered = [x / num_of_visits for x in encountered]
    return encountered

if __name__ == "__main__":
    print(test_pr_matrix())
