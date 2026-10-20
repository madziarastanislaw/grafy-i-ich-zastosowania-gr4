import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

def random_euler_sequence(n):
    if n < 5:
        raise ValueError("Wymagane n >= 5")

    possible = list(range(2, n, 2))

    times = 0
    while times <= 10:
        seq = [random.choice(possible) for _ in range(n)]
        times += 1
        if max(seq) > 2 and nx.is_graphical(seq):
            return seq
    return False

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

n = int(sys.argv[1])
G = make_graph(random_euler_sequence(n))
if not G:
    pass
else:
    L = list(nx.eulerian_circuit(G))
    str = f"{L[0][0]} -> {L[0][1]} "
    L.pop(0)
    for i in L:
        str += f"-> {i[1]} "
    print(str)
    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()