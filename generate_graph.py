import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections
import itertools
from networkx import MultiDiGraph

def union_find(n):
    def find(x):
        if x != parents[x]:
            result = find(parents[x])
            parents[x] = result
            return result
        return x

    def union(x, y):
        rx = find(x)
        ry = find(y)
        if rx == ry:
            return False
        if rank[rx] > rank[ry]:
            parents[ry] = rx
        else:
            parents[rx] = ry
            if rank[rx] == rank[ry]:
                rank[ry] += 1
        return True

    parents = [i for i in xrange(n)]
    rank = [0 for i in xrange(n)]

    return find, union

def dist(a, b):
    a0, a1 = a
    b0, b1 = b
    return np.sqrt((a0 - b0) ** 2 + (a1 - b1) ** 2)

def total_dist(L):
    prev = None
    total_dist = 0
    for coord in L:
        if prev != None:
            total_dist += dist(prev, coord)
        prev = coord

def optimal_order(L):
    n = len(L)
    elem_map = {L[i] : i for i in xrange(n)}
    index_map = {i : L[i] for i in xrange(n)}
    cache_dist = {}
    for i1, i2 in itertools.combinations(xrange(n), r=2):
        cache_dist[(i1, i2)] = dist(index_map[i1], index_map[i2])
    dist_index_list = sorted([(cache_dist[key], key) for key in cache_dist])
    index = 0
    found = 0
    neighbors = {}
    find, union = union_find(n)
    while found < n - 1:
        distance, (node1, node2) = dist_index_list[index]
        if union(node1, node2):
            for (n1, n2) in ((node1, node2), (node2, node1)):
                if n1 not in neighbors:
                    neighbors[n1] = []
                neighbors[n1].append(n2)
            found += 1
        index += 1
    start = None
    for key, L in neighbors.iteritems():
        if len(L) == 1:
            start = key
            break
    Q = [start]
    L = []
    found = [0 for _ in xrange(n)]
    while len(Q) > 0:
        node = Q.pop()
        found[node] = True
        L.append(index_map[node])
        children = neighbors[node]
        # assert(len(children) <= 2)
        Q += [child for child in children if not found[child]]
    return L

def in_range(lat, lng, lat_range, lng_range):
    return lat_range[0] < lat < lat_range[1] and lng_range[0] < lng < lng_range[1]


# Code to plot the initial data that I got, see below for the new data part
def parse_old_data_to_graph(lat_range, lng_range, max_road_distance):
    strt_dict = {}
    # maps coordinates to streets at those coordinates
    labeled_coords = {}

    with open('intersection_data.csv', 'r') as int_dest_old:
        for line in int_dest_old:
            st1, st2, lat, lng = line.rstrip().split(',')
            try:
                lat, lng = float(lat), float(lng)
                coord = (lng, lat)
                if in_range(lat, lng, lat_range, lng_range):
                    if coord in labeled_coords:
                        continue
                    labeled_coords[coord] = []
                    sts = set(st1.split(' \ ')) | set(st2.split(' \ '))
                    for st in sts:
                        if st not in strt_dict:
                            strt_dict[st] = set()
                        strt_dict[st].add(coord)
                        labeled_coords[coord].append(st)
            except ValueError:
                pass
    labeled_edges = []
    # use (lng, lat) as indices of an adjancency list to map connection
    labeled_adj_list = {}
    for coord in labeled_coords:
        labeled_adj_list[coord] = []
    for st, ints in strt_dict.iteritems():
        order0 = sorted(ints, key=lambda coord: coord[0])
        order1 = sorted(ints, key=lambda coord: coord[1])
        if order0[0] != order1[0]:
            order1 = list(reversed(order1))
        correct_list = order0
        for coord0, coord1 in itertools.izip(order0, order1):
            if coord0 != coord1:
                dist0 = total_dist(order0)
                dist1 = total_dist(order1)
                correct_list = order0 if dist0 < dist1 else order1
                correct_list = optimal_order(correct_list)
                break
        prev = None
        for coord in correct_list:
            if prev != None:
                if dist(coord, prev) < max_road_distance:
                    labeled_edges.append((prev, coord))
                    labeled_adj_list[prev].append(coord)
                    labeled_adj_list[coord].append(prev)
            prev = coord
    return labeled_coords, labeled_adj_list


def real_lng(x): # translates the unit used by the new dataset to longitude
    return 1.8058362e-4 * x - 123.020261

def real_lat(x): # translates the unit used by the new dataset to latitude
    return -1.413746e-4 * x + 38.31506813

def parse_SF_data_to_graph(lat_range, lng_range):
    # a list of (coordinatex, coordinatey) -- id is the index in coords
    # id's are reassigned since we don't care about the roads outside of SF -- there would be too many roads
    coords = []
    old_id_to_id = {} # maps original id from the file to new id (index of the coordinate in coords)
    adjancency_list = {} # maps new id to adjacent new ids

    # record nodes
    with open('SF_nodes.txt', 'r') as node_file:
        for line in node_file:
            nid, x, y = line.rstrip().split(' ')
            lng, lat = real_lng(float(x)), real_lat(float(y)) # translate their unit into actual latitude and longitude
            if in_range(lat, lng, lat_range, lng_range): # Only keep the roads in SF
                old_id_to_id[nid] = len(coords)
                coords.append((lng, lat))

    # record edges
    for id in xrange(len(coords)):
        adjancency_list[id] = []
    with open('SF_edges.txt', 'r') as edge_file:
        for line in edge_file:
            _eid, nid1, nid2, _dist = line.rstrip().split(' ')
            if nid1 in old_id_to_id and nid2 in old_id_to_id:
                new_id1 = old_id_to_id[nid1]
                new_id2 = old_id_to_id[nid2]
                # add to adjacency list in terms of the new id of the nodes
                adjancency_list[new_id1].append(new_id2)
                adjancency_list[new_id2].append(new_id1)
    return coords, adjancency_list

def map_intersection_names(old_coords, old_adj_list, new_coords, new_adj_list, threshold=0.0002):
    # try to match the new dataset intersection location with the original dataset to obtain road names
    new_labeled_id = [None for _ in xrange(len(new_coords))]
    sorted_coords = sorted(new_coords)
    coords_to_match = []
    for labeled_coord, label in old_coords.iteritems():
        first = 0
        last = len(sorted_coords) - 1
        coordx, coordy = labeled_coord
        while last - first > 1:
            mid = (first + last) // 2
            midpoint = sorted_coords[mid]
            if midpoint[0] > coordx - threshold:
                last = mid
            else:
                first = mid
        closest = None
        two_tries = True
        while (two_tries or abs(sorted_coords[first][0] - coordx) < threshold) and first < len(sorted_coords):
            if abs(sorted_coords[first][1] - coordy) < threshold:
                closest = first
            two_tries = False
            first += 1
        if closest != None:
            new_labeled_id[closest] = label
            coords_to_match.append((labeled_coord, closest))
    matched_coords = {}
    matched_ids = [False for _ in xrange(len(new_coords))]
    threshold = 0.0005
    # propagate the matching as much as possible from the matched intersections
    for labeled_coord, new_id in coords_to_match:
        labeled_neighbors = old_adj_list[labeled_coord][:]
        new_neighbor_ids = new_adj_list[new_id][:]
        best_match = None
        min_distance = float('inf')
        changed = True
        while changed:
            changed = False
            for new_neighbor_id in new_neighbor_ids:
                if matched_ids[new_neighbor_id]:
                    continue
                new_neighbor = new_coords[new_neighbor_id]
                for old_neighbor in labeled_neighbors:
                    if old_neighbor in matched_coords:
                        continue
                    if abs(old_neighbor[0] - new_neighbor[0]) < threshold and abs(old_neighbor[1] - new_neighbor[1]) < threshold:
                        curr_dist = dist(old_neighbor, new_neighbor)
                        if curr_dist < min_distance:
                            min_distance = curr_dist
                            best_match = (old_neighbor, new_neighbor_id)
                            changed = True
            if changed:
                old_neighbor, new_neighbor_id = best_match
                matched_coords[old_neighbor] = True
                matched_ids[new_neighbor_id] = True
                new_labeled_id[new_neighbor_id] = old_coords[old_neighbor]
                new_neighbor_ids.remove(new_neighbor_id)
                labeled_neighbors.remove(old_neighbor)
                min_distance = float('inf')
                coords_to_match.append((old_neighbor, new_neighbor_id))
    return new_labeled_id

def adj_list_to_edge_list(coords, adj_list):
    edge_list = set()
    for x, yList in adj_list.iteritems():
        for y in yList:
            edge_list.add((coords[x], coords[y]))
    return edge_list

# plot the points given a list of coordinates with id as indices and a list of edges
def plot_graph(coords, coord_labels, node_weights, edge_list, edge_weight):
    fig, ax = plt.subplots()
    ax.scatter(*itertools.izip(*coords), c=node_weights, s=50, picker=True)
    ax.add_collection(collections.LineCollection(edge_list))
    ax.autoscale()
    ax.margins(0.1)

    def on_pick(event): # can click the points to see new id, coordinate, and label (if any)
        for ind in event.ind:
            coord = coords[ind]
            label = coord_labels[ind]
            weight = node_weights[ind]
            print ind, coord, weight, label

    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()

# what you guys probably are going to use, see their respective comments above
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

def convert_to_graph(coords, adjacency_list):
    # entries are [forward node, reversed node]
    node_mappings = [[None, None] for _ in xrange(len(coords))]
    graph = MultiDiGraph()
    for k in adjacency_list:
        node_to_add = Node(k, 0)
        node_mappings[k][0] = node_to_add
        node_to_add.x, node_to_add.y = coords[k]
        graph.add_node(node_to_add)
    for k in adjacency_list:
        edge_node_1 = node_mappings[k][0]
        # graph.add_edge(edge_node_1, edge_node_1)
        for neighbor in adjacency_list[k]:
            edge_node_2 = node_mappings[neighbor][0]
            if graph.has_edge(edge_node_1, edge_node_2):
                continue
            else:
                graph.add_edge(edge_node_1, edge_node_2)

    reverse_graph = graph.reverse(copy=True)
    for node in reverse_graph.nodes_iter():
        node_to_add = Node(node.id, 1)
        node_mappings[node.id][1] = node_to_add
        node_to_add.x, node_to_add.y = node.x, node.y
        graph.add_node(node_to_add)
    for node in reverse_graph.nodes_iter():
        edge_node_1 = node_mappings[node.id][0]   #Node(node.id, True)
        for n in reverse_graph.neighbors(node):
            edge_node_2 = node_mappings[n.id][1]
            graph.add_edge(edge_node_1, edge_node_2)
    for node in reverse_graph.nodes_iter():
        edge_node_1 = node_mappings[node.id][0]
        edge_node_2 = node_mappings[node.id][1]
        graph.add_edge(edge_node_1, edge_node_2)
        graph.add_edge(edge_node_2, edge_node_1)
    # print graph.nodes()
    return graph, node_mappings

