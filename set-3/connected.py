import matplotlib.pyplot as plt
import networkx as nx
import random
import sys
import os
import re

#importy z poprzednich zestawów
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "set-2"))
from seq import components #set-2, zad. 3 - spójne składowe

INT_RE = re.compile(r"-?\d+")                 #liczba całkowita, np. 12
FLOAT_RE = re.compile(r"-?(\d+\.\d*|\.\d+)")  #ułamek dziesiętny, np. 0.3, .5, 1.


def parse_int(s):
    #akceptuje wyłącznie zapis całkowity (bez 1e3, 1_000, +5, spacji itp.)
    if not INT_RE.fullmatch(s):
        raise ValueError(f"'{s}' is not an integer!")
    return int(s)

def parse_edges_or_prob(s):
    #int -> liczba krawędzi G(n,l), ułamek dziesiętny -> prawdopodobieństwo G(n,p); nic innego (1e-1, inf, nan...)
    if INT_RE.fullmatch(s):
        return int(s)
    if FLOAT_RE.fullmatch(s):
        return float(s)
    raise ValueError(f"'{s}' is neither an integer (edges) nor a decimal number (probability)!")


#Zastępuje set-1 zad. 3 - generowanie grafów losowych zaimplementowane ręcznie (model Erdősa-Rényiego)
def random_graph(N, MP):
    #MP jako float -> G(n,p), jako int -> G(n,l); wierzchołki numerowane 1..N
    if N < 1:
        raise ValueError("Number of nodes must be at least 1!")

    G = nx.Graph()
    G.add_nodes_from(range(1, N+1))
    pairs = [(i, j) for i in range(1, N+1) for j in range(i+1, N+1)] #wszystkie N(N-1)/2 możliwych krawędzi

    if isinstance(MP, float):
        #G(n,p): każda para wierzchołków niezależnie łączona krawędzią z prawdopodobieństwem p
        if MP < 0 or MP > 1:
            raise ValueError("Probability must be in range [0, 1]!")
        for u, v in pairs:
            if random.random() < MP:
                G.add_edge(u, v)
        return G

    #G(n,l): l krawędzi wybranych jednostajnie spośród wszystkich par (każdy taki graf równie prawdopodobny)
    if MP < 0 or MP > len(pairs):
        raise ValueError(f"Number of edges must be in range [0, {len(pairs)}]!")
    #częściowe tasowanie Fishera-Yatesa - pierwsze l pozycji to losowa l-elementowa podlista par
    for k in range(MP):
        r = random.randint(k, len(pairs)-1)
        pairs[k], pairs[r] = pairs[r], pairs[k]
        G.add_edge(*pairs[k])
    return G


def random_connected_graph(N, MP, tries=100):
    #zwraca wyłącznie spójny graf losowy o dokładnie N wierzchołkach (numerowanych od 1)
    #MP jako float -> G(n,p), jako int -> G(n,l); po nieudanych próbach rzuca ValueError
    if isinstance(MP, int) and MP < N-1:
        raise ValueError(f"Connected graph with {N} nodes needs at least {N-1} edges!")

    for _ in range(tries):
        G = random_graph(N, MP)
        if len(components(G)) == 1: #jedna spójna składowa = graf spójny
            #reszta kodu (macierz wag, centra) zakłada wierzchołki dokładnie 1..N
            if sorted(G.nodes) != list(range(1, N+1)):
                raise RuntimeError("Generated graph nodes are not numbered 1..N!")
            return G

    raise ValueError(f"Could not draw a connected graph in {tries} tries - try more edges / higher probability.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: connected.py <nodes> <edges (int) | probability (float)>")
        sys.exit(1)

    try:
        N = parse_int(sys.argv[1])
        MP = parse_edges_or_prob(sys.argv[2])
    except ValueError as e:
        print(e)
        sys.exit(1)

    try:
        G = random_connected_graph(N, MP)
    except ValueError as e:
        print(e)
        sys.exit(1)

    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()
