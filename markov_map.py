from generate_graph import *
from generate_prob import *
from pagerank import *
import scipy
import math
from pprint import pprint

lat_range = [37.7, 37.85]
lng_range = [-122.60, -122.35]
bus_lat_range = [37.75, 37.81]
bus_lng_range = [-122.45, -122.375]
max_road_distance = float('inf') # 0.007

print 'parsing old dataset'
old_coords, old_adj_list = parse_old_data_to_graph(lat_range, lng_range, max_road_distance)
print 'parsing new dataset'
coords, adj_list = parse_SF_data_to_graph(lat_range, lng_range, 'SF_nodes.txt', 'SF_edges.txt')
highway_coords, highway_adj = parse_SF_data_to_graph(lat_range, lng_range, 'CA_nodes.txt', 'CA_edges.txt')
print 'labeling new dataset from old dataset'
ids_to_labels = map_intersection_names(old_coords, old_adj_list, coords, adj_list)

edge_list = adj_list_to_edge_list(coords, adj_list)
highway_edge_list = adj_list_to_edge_list(highway_coords, highway_adj)
# plot_graph(coords, ids_to_labels, edge_list)

businesses = parse_businesses('business_locations_data.txt')
businesses = [((lng, lat), weight) for (lng, lat), weight in businesses if in_range(lat, lng, bus_lat_range, bus_lng_range)]
print 'starting to convert'
graph, node_mapping = convert_to_graph(coords, adj_list)

print 'graph generated. scoring nodes.'
score_nodes(graph, businesses)
determine_capacities(graph, highway_adj, highway_coords)


# Random
# plot_graph(highway_coords, None, None, highway_edge_list, None, 'r')
# for node in graph:
# 	node.score = 1
# 	node.factors['hwy_dist'] = 1
# node_weights = crawl(graph, node_mapping, int(1e6), 0.01)
# normalized_weights = [0 for _ in xrange(len(coords))]
# for node in graph:
# 	normalized_weights[node.id] = node_weights[node.id] / node.factors['capacity']

# total_dispersion = -sum([math.log(x) * x for x in normalized_weights])

# print total_dispersion
# plot_graph(coords, ids_to_labels, normalized_weights, edge_list, None, event=True)
# plot_businesses(businesses)
# plt.show()



node_weights = crawl(graph, node_mapping, int(1e6), 0.01)

normalized_weights = [0 for _ in xrange(len(coords))]
for node in graph:
	normalized_weights[node.id] = node_weights[node.id] / node.factors['capacity']

sorted_weights = sorted([(weight, i) for i, weight in enumerate(normalized_weights)], reverse=True)
most_impacted = sorted_weights[:10]
for weight, i in most_impacted:
	print weight, ids_to_labels[i], coords[i]

# total_dispersion = -sum([math.log(x) * x for x in normalized_weights])
# print total_dispersion


# # Resolving the 30 most impacted nodes
# most_impacted_id = [x[1] for x in most_impacted]
# for node in graph:
# 	if node.id in most_impacted_id:
# 		node.factors['capacity'] += 0.5

# node_weights = crawl(graph, node_mapping, int(1e6), 0.01)
# for node in graph:
# 	normalized_weights[node.id] = node_weights[node.id] / node.factors['capacity']
# total_dispersion = -sum([math.log(x) * x for x in normalized_weights])

# print total_dispersion



plot_graph(highway_coords, None, None, highway_edge_list, None, 'r')
plot_graph(coords, ids_to_labels, normalized_weights, edge_list, None, event=True)
plot_businesses(businesses)
plt.show()

# eigvals, eigvecs = scipy.sparse.linalg.eigs(pr_mat)
# D = np.zeros((n, n), dtype='complex64')
# D[:n, :n] = np.diag(eigvals)
# print eigvals
# p = 8
# print(np.dot(eigvecs, np.dot(np.power(D, p), np.linalg.inv(eigvecs))))
# print(np.linalg.matrix_power(matrix, p))