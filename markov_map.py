from generate_graph import *
from generate_prob import *
from pagerank import *

lat_range = [37.7, 37.85]
lng_range = [-122.60, -122.35]
max_road_distance = float('inf') # 0.007

print 'parsing old dataset'
old_coords, old_adj_list = parse_old_data_to_graph(lat_range, lng_range, max_road_distance)
print 'parsing new dataset'
coords, adj_list = parse_SF_data_to_graph(lat_range, lng_range)
print 'labeling new dataset from old dataset'
ids_to_labels = map_intersection_names(old_coords, old_adj_list, coords, adj_list)

# plot_graph(coords, ids_to_labels, adj_list_to_edge_list(coords, adj_list))

print 'starting to convert'
graph = convert_to_graph(coords, adj_list)
print 'graph generated. plotting now'

# assign node values
for node in graph:
	node.score = 1
print(len(graph))
for node in graph:
	if node.score != 1:
		print "Not 1"

pr_mat = create_pr_matrix(graph)

# from networkx_viewer import Viewer
# app = Viewer(graph)
# app.mainloop()
# networkx.draw(graph)
# print 'displaying plot.'
# plt.show()