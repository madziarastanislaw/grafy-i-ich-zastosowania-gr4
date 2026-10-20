import networkx as nx
import matplotlib.pyplot as plt
import sys

def make_graph(seq):
    def sort_elem(T: list):
        return T[0] #założenie, że indeks jest na 1, a stopień na 0

    act_seq = []
    for idx in range(0,len(seq)):
        act_seq.append([seq[idx],idx])

    if seq == False:
        print("Creation took too long. Aborting.")
        return False
    
    G = nx.Graph()
    G.add_nodes_from([i for i in range(0, len(seq))])
    edges = []
    while True:
        act_seq.sort(reverse=True, key=sort_elem)
        if act_seq[0][0] == 0:
            G.add_edges_from(edges)
            return G
        for i in range(1,act_seq[0][0]+1):
            if act_seq[i][0] == 0:
                return False
            edges.append([act_seq[0][1],act_seq[i][1]])
            act_seq[i][0] -=  1
        act_seq[0][0] = 0


N = int(sys.argv[1])
K = int(sys.argv[2])

if K > N-1:
    print("Degree cannot be larger tha the ammount of nodes!")
    sys.exit(1)

seq = [K for _ in range(0, N)]
G = make_graph(seq)

if not G:
    pass
else:
    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()