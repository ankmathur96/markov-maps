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
max_road_distance = 0.007
int_dict = {}
strt_dict = {}
coords = {}
with open('intersection_data.csv', 'r') as int_dest_old:
    for line in int_dest_old:
        st1, st2, lat, lng = line.rstrip().split(',')
        try:
            lat, lng = float(lat), float(lng)
            coord = (lng, lat)
            if lat_range[0] < lat < lat_range[1] and lng_range[0] < lng < lng_range[1]:
                if coord in coords:
                    # print 'skipped %s %s' % (st1, st2)
                    continue
                coords[coord] = []
                # int_dict[(st1, st2)] = coord
                sts = set(st1.split(' \ ')) | set(st2.split(' \ '))
                for st in sts:
                    if st not in strt_dict:
                        strt_dict[st] = set()
                    strt_dict[st].add(coord)
                    coords[coord].append(st)
        except ValueError:
            pass
edges = []
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
                edges.append((prev, coord))
        prev = coord

coord_list = list(coords.keys())
roads = collections.LineCollection(edges)
fig, ax = plt.subplots()
ax.scatter(*itertools.izip(*coord_list), picker=True)
ax.add_collection(roads)
ax.autoscale()
ax.margins(0.1)

def on_pick(event):
    for ind in event.ind:
        coord = coord_list[ind]
        print coords[coord], coord
fig.canvas.mpl_connect('pick_event', on_pick)

# plt.plot((0, 1), (1, 3))
# plt.scatter(*zip(*int_dict.values()))
# for streets, (x, y) in int_dict.iteritems():
#     label = str(streets)
#     plt.annotate(
#         label, 
#         xy = (x, y), xytext = (-20, 20),
#         textcoords = 'offset points')
plt.show()