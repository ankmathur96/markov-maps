import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections
import pprint
from itertools import izip

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

int_dict = {}
strt_dict = {}
lat_range = [37.7, 37.85]
lng_range = [-122.60, -122.35]
coords = set()
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
                coords.add(coord)
                # int_dict[(st1, st2)] = coord
                sts = set(st1.split(' \ ')) | set(st2.split(' \ '))
                for st in sts:
                    if st not in strt_dict:
                        strt_dict[st] = set()
                    strt_dict[st].add(coord)
        except ValueError:
            pass
edges = []
for st, ints in strt_dict.iteritems():
    order0 = sorted(ints, key=lambda coord: coord[0])
    order1 = sorted(ints, key=lambda coord: coord[1])
    if order0[0] != order1[0]:
        order1 = reversed(order1)
    correct_list = order0
    for coord0, coord1 in izip(order0, order1):
        if coord0 != coord1:
            dist0 = total_dist(order0)
            dist1 = total_dist(order1)
            correct_list = order0 if dist0 < dist1 else order1
            break
    prev = None
    for coord in correct_list:
        if prev != None:
            edges.append((prev, coord))
        prev = coord

roads = collections.LineCollection(edges)
fig, ax = plt.subplots()
ax.add_collection(roads)
ax.autoscale()
ax.margins(0.1)
# plt.scatter(*zip(*int_dict.values()))
# for streets, (x, y) in int_dict.iteritems():
#     label = str(streets)
#     plt.annotate(
#         label, 
#         xy = (x, y), xytext = (-20, 20),
#         textcoords = 'offset points')
plt.show()