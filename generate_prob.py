#graph is a networkx graph
#business_locs is a dictionary of {zipcode: (x,y,n=number_in_zipcode))}
def score_nodes(graph, business_locs):
    for node in graph.nodes():
        for zipcode in business_locs:
            zip_data = business_locs[zipcode]
            x, y, n = get_zip_x(zip_data), get_zip_y(zip_data), get_zip_num(zip_data)
            node.score = score_func(l2_norm((node.x, node.y), (x, y)), n)

#graph is a networkx graph
#node is networkx node
#returns a dictionary of {neighbor: node to neighbor transition prob}
def get_node_to_neighbors_prob(graph, node):
    trans_prob_dict = {}
    neighbors = graph.neighbors(node)
    sum_neighbor_score = 0
    for neighbor in neighbors:
        sum_neighbor_score += neighbor.score
    for neighbor in neighbors:
        trans_prob_dict[neighbor] = neighbor.score / sum_neighbor_score
    return trans_prob_dict
        
def get_zip_x((x, y, n)):
    return x

def get_zip_y((x, y, n)):
    return y

def get_zip_num((x, y, n)):
    return n

def l2_norm(pt1, pt2):
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**(0.5)

def score_func(x,n):
    return n / x