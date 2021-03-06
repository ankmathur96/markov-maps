from generate_graph import *
from generate_prob import *
from pagerank import *
import math
from pprint import pprint
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# boxed/limited range
lat_range = [37.7, 37.85]
lng_range = [-122.60, -122.35]
bus_lat_range = [37.75, 37.81]
bus_lng_range = [-122.45, -122.375]
max_road_distance = float('inf') # 0.007

print 'parsing old dataset'
old_coords, old_adj_list = parse_old_data_to_graph(lat_range, lng_range, max_road_distance)
print 'parsing new dataset'
coords, adj_list = parse_SF_data_to_graph(lat_range, lng_range, 'data/SF_nodes.txt', 'data/SF_edges.txt')
highway_coords, highway_adj = parse_SF_data_to_graph(lat_range, lng_range, 'data/CA_nodes.txt', 'data/CA_edges.txt')
print 'labeling new dataset from old dataset'
ids_to_labels = map_intersection_names(old_coords, old_adj_list, coords, adj_list)

edge_list = adj_list_to_edge_list(coords, adj_list)
highway_edge_list = adj_list_to_edge_list(highway_coords, highway_adj)
# plot_graph(coords, ids_to_labels, edge_list)

businesses = parse_businesses('data/business_locations_data.txt')
businesses = [((lng, lat), weight) for (lng, lat), weight in businesses if in_range(lat, lng, bus_lat_range, bus_lng_range)]
print 'starting to convert'
graph, node_mapping = convert_to_graph(coords, adj_list)

print 'graph generated. scoring nodes.'
score_nodes(graph, businesses)
determine_capacities(graph, highway_adj, highway_coords)


def plot_results(node_weights):
	normalized_weights = [0 for _ in xrange(len(coords))]
	for node in graph:
		normalized_weights[node.id] = node_weights[node.id] / node.factors['capacity']

	# sorted_weights = sorted([(weight, i) for i, weight in enumerate(normalized_weights)], reverse=True)
	# most_impacted = sorted_weights[:10]
	# for weight, i in most_impacted:
	# 	print weight, ids_to_labels[i], coords[i]
	plot_graph(coords, ids_to_labels, normalized_weights, edge_list, None, event=True)
	plot_graph(highway_coords, None, None, highway_edge_list, None, 'r')
	plot_businesses(businesses)
	
	plt.draw()
	time.sleep(0.1)
	plt.pause(0.1)

mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.ion()
plt.show()
node_weights = crawl(graph, node_mapping, int(5e5), 0.01, plot_results)


# eigvals, eigvecs = scipy.sparse.linalg.eigs(pr_mat)
# D = np.zeros((n, n), dtype='complex64')
# D[:n, :n] = np.diag(eigvals)
# print eigvals
# p = 8
# print(np.dot(eigvecs, np.dot(np.power(D, p), np.linalg.inv(eigvecs))))
# print(np.linalg.matrix_power(matrix, p))