from __future__ import division
import math
HWY_CAP = 8
ROAD_CAP = 2

#graph is a networkx graph
#business_locs is a dictionary of {zipcode: (x,y,n=number_in_zipcode))}
def score_nodes(graph, business_locs):
    for node in graph:
        neighbor_dists = []
        for location, weight in business_locs:
            neighbor_dists.append(score_func(l2_norm((node.x, node.y), location), weight))
        node.score = max(neighbor_dists)

#graph is a networkx graph
#node is networkx node
#returns a dictionary of {neighbor: node to neighbor transition prob}
def get_node_to_neighbors_prob(graph, node):
    trans_prob_dict = {}
    neighbors = graph.neighbors(node)
    sum_hwy_score = 0
    neighbor_scores = []
    for neighbor in neighbors:
        neighbor_scores.append(neighbor.score)
        sum_hwy_score += neighbor.factor['hwy_dist']
    sum_neighbor_score = sum(neighbor_scores)
    avg_neighbor_score = sum_neighbor_score / len(neighbor_scores)
    neighbor_scores = [x - avg_neighbor_score for x in neighbor_scores]
    min_score = 3 * math.abs(min(neighbor_scores))
    neighbor_scores = [x + min_score for x in neighbor_scores]
    for neighbor in neighbors:
        trans_prob_dict[neighbor] = 0.7 * (neighbor.score / sum_neighbor_score) + 0.3 * (neighbor.factors['hwy_dist'] / sum_hwy_score)
    return trans_prob_dict

def get_hwy_dist(n_coord, h_coord1, h_coord2, connected):
    if connected:
        x0, y0 = n_coord
        x1, y1 = h_coord1
        x2, y2 = h_coord2
        return abs((y2-y1)*x0 - (x2-x1) * y0 + x2*y1 - y2*x1)/l2_norm(h_coord1, h_coord2)
    else:
        return l2_norm(n_coord, h_coord1)

def assign_capacity(closest_dist):
    if closest_dist < 0.001:
        capacity = HWY_CAP
    else:
        capacity = ROAD_CAP
    return capacity / HWY_CAP

def determine_capacities(graph, highway_adj, highway_coords):
    for n in graph:
        h_dist = sorted([(l2_norm((n.x, n.y), node), index) for index, node in enumerate(highway_coords)])
        (dist1, n1), (dist2, n2) = h_dist[:2]
        closest_dist = get_hwy_dist((n.x, n.y), highway_coords[n1], highway_coords[n2], n1 in highway_adj[n2])
        n.factors['capacity'] = assign_capacity(closest_dist)
        n.factors['hwy_dist'] = closest_dist

#### UTILS:
def l2_norm(pt1, pt2):
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**(0.5)

def score_func(x, n):
    return n / (0.01 + x)