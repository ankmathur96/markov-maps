import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections
import pprint
import itertools

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


lat_range = [37.7, 37.85]
lng_range = [-122.60, -122.35]

def in_range(lat, lng):
    return lat_range[0] < lat < lat_range[1] and lng_range[0] < lng < lng_range[1]


# Code to plot the initial data that I got, see below for the new data part

max_road_distance = float('inf') # 0.007
strt_dict = {}
labeled_coords = {}

with open('intersection_data.csv', 'r') as int_dest_old:
    for line in int_dest_old:
        st1, st2, lat, lng = line.rstrip().split(',')
        try:
            lat, lng = float(lat), float(lng)
            coord = (lng, lat)
            if in_range(lat, lng):
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

# labeled_coord_list = list(labeled_coords.keys())
# fig, ax = plt.subplots()
# ax.scatter(*itertools.izip(*labeled_coord_list), picker=True)
# ax.add_collection(collections.LineCollection(labeled_edges))
# ax.autoscale()
# ax.margins(0.1)

# def on_pick(event):
#     for ind in event.ind:
#         coord = labeled_coord_list[ind]
#         print labeled_coords[coord], coord
# fig.canvas.mpl_connect('pick_event', on_pick)



# Code to plot and record from the new files that Eli found

# a list of (original id from the file, (coordinatex, coordinatey)) -- new id is the index in coords
# id's are reassigned since we don't care about the roads outside of SF -- there would be too many roads
coords = []
old_id_to_id = {} # maps original id from the file to new id (index of the coordinate in coords)
edge_list = [] # used for plotting purposes
adjancency_list = {} # maps new id to adjacent new ids

def real_lng(x): # translates the unit used by the new dataset to longitude
    return 1.8058362e-4 * x - 123.020261

def real_lat(x): # translates the unit used by the new dataset to latitude
    return -1.413746e-4 * x + 38.31506813

# record nodes
with open('SF_nodes.txt', 'r') as node_file:
    for line in node_file:
        nid, x, y = line.rstrip().split(' ')
        lng, lat = real_lng(float(x)), real_lat(float(y)) # translate their unit into actual latitude and longitude
        if in_range(lat, lng): # Only keep the roads in SF
            old_id_to_id[nid] = len(coords)
            coords.append((nid, (lng, lat)))

# record edges
for id in xrange(len(coords)):
    adjancency_list[id] = []
with open('SF_edges.txt', 'r') as edge_file:
    for line in edge_file:
        _eid, nid1, nid2, _dist = line.rstrip().split(' ')
        if nid1 in old_id_to_id and nid2 in old_id_to_id:
            new_id1 = old_id_to_id[nid1]
            new_id2 = old_id_to_id[nid2]
            (old_id1, coord1) = coords[new_id1]
            (old_id2, coord2) = coords[new_id2]
            # add to adjacency list in terms of the new id of the nodes
            adjancency_list[new_id1].append(new_id2)
            adjancency_list[new_id2].append(new_id1)
            edge_list.append((coord1, coord2))

# try to match the new dataset intersection location with the original dataset to obtain road names
new_labeled_id = [None for _ in xrange(len(coords))]
sorted_pairs = sorted([(coord, id) for id, (old_id, coord) in enumerate(coords)])
sorted_coords, sorted_ids = zip(*sorted_pairs)
threshold = 0.0002
coords_to_match = []
for labeled_coord, label in labeled_coords.iteritems():
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
matched_ids = [False for _ in xrange(len(coords))]
threshold = 0.0005
# propagate the matching as much as possible from the matched intersections
for labeled_coord, new_id in coords_to_match:
    labeled_neighbors = labeled_adj_list[labeled_coord][:]
    new_neighbor_ids = adjancency_list[new_id][:]
    best_match = None
    min_distance = float('inf')
    changed = True
    while changed:
        changed = False
        for new_neighbor_id in new_neighbor_ids:
            if matched_ids[new_neighbor_id]:
                continue
            new_neighbor = coords[new_neighbor_id][1]
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
            new_labeled_id[new_neighbor_id] = labeled_coords[old_neighbor]
            new_neighbor_ids.remove(new_neighbor_id)
            labeled_neighbors.remove(old_neighbor)
            min_distance = float('inf')
            coords_to_match.append((old_neighbor, new_neighbor_id))

# plot the points
fig, ax = plt.subplots()
ax.scatter(*itertools.izip(*sorted_coords), picker=True)
ax.add_collection(collections.LineCollection(edge_list))
ax.autoscale()
ax.margins(0.1)
def on_pick(event): # can click the points to see new id, coordinate, and label (if any)
    for ind in event.ind:
        coord = sorted_coords[ind]
        newid = sorted_ids[ind]
        label = new_labeled_id[newid]
        print newid, coord, label
fig.canvas.mpl_connect('pick_event', on_pick)
plt.show()

# what you guys probably are going to use, see their respective comments above
coords = coords
adjancency_list = adjancency_list 
