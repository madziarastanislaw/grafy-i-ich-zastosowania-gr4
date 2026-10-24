import matplotlib.pyplot as plt
import networkx as nx
import sys
import os

#importy z poprzednich zestawów
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "set-1"))
sys.path.insert(0, os.path.join(BASE, "..", "set-2"))
from randoming import random_graph #set-1, zad. 3 - G(n,l) / G(n,p)
from seq import components #set-2, zad. 3 - spójne składowe


def random_connected_graph(N, MP, tries=100):
    #zwraca wyłącznie spójny graf losowy o dokładnie N wierzchołkach (numerowanych od 1)
    #MP jako float -> G(n,p), jako int -> G(n,l); po nieudanych próbach rzuca ValueError
    if isinstance(MP, int) and MP < N-1:
        raise ValueError(f"Connected graph with {N} nodes needs at least {N-1} edges!")

    for _ in range(tries):
        G = random_graph(N, MP)
        if len(components(G)) == 1: #jedna spójna składowa = graf spójny
            return nx.relabel_nodes(G, {v: v+1 for v in G.nodes})

    raise ValueError(f"Could not draw a connected graph in {tries} tries - try more edges / higher probability.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: connected.py <nodes> <edges (int) | probability (float)>")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        if '.' in sys.argv[2]:
            MP = float(sys.argv[2])
        else:
            MP = int(sys.argv[2])
    except ValueError:
        print("Input values must be an integer and integer/float")
        sys.exit(1)

    try:
        G = random_connected_graph(N, MP)
    except ValueError as e:
        print(e)
        sys.exit(1)

    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()
