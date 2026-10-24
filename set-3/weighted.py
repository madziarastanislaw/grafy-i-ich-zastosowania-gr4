import matplotlib.pyplot as plt
import networkx as nx
import random
import sys

from connected import random_connected_graph #korzysta z set-1 i set-2

INF = float("inf")


#Zadanie 1 - spójny graf losowy z wagami 1-10
def connected_weighted_graph(N, MP):
    G = random_connected_graph(N, MP)
    for u, v in G.edges:
        G[u][v]["weight"] = random.randint(1, 10)
    return G

def weight_matrix(G):
    #w[u][v] - waga krawędzi (u,v), indeksy od 1 (wiersz/kolumna 0 nieużywane)
    n = len(G)
    w = [[INF]*(n+1) for _ in range(n+1)]
    for u, v, data in G.edges(data=True):
        w[u][v] = data["weight"]
        w[v][u] = data["weight"]
    return w


#Zadanie 2 - algorytm Dijkstry (alg. 1-3 z alg_3.pdf)
def dijkstra(G, w, s):
    ds = {}
    ps = {}

    def init(G, s):
        for v in G.nodes:
            ds[v] = INF
            ps[v] = None
        ds[s] = 0

    def relax(u, v, w):
        if ds[v] > ds[u] + w[u][v]:
            ds[v] = ds[u] + w[u][v]
            ps[v] = u

    init(G, s)
    S = set()
    while len(S) != len(G):
        u = min((v for v in G.nodes if v not in S), key=lambda v: ds[v])
        S.add(u)
        for v in G[u]:
            if v not in S:
                relax(u, v, w)
    return ds, ps

def get_path(ps, v):
    path = []
    while v is not None:
        path.append(v)
        v = ps[v]
    return path[::-1]


#Zadanie 3 - macierz odległości (Dijkstra z każdego wierzchołka)
def distance_matrix(G, w):
    nodes = sorted(G.nodes)
    D = []
    for s in nodes:
        ds, _ = dijkstra(G, w, s)
        D.append([ds[v] for v in nodes])
    return D


#Zadanie 4 - centrum i centrum minimax
def centers(D):
    sums = [sum(row) for row in D]
    maxs = [max(row) for row in D]
    c = sums.index(min(sums))
    cm = maxs.index(min(maxs))
    return (c+1, sums[c]), (cm+1, maxs[cm])


#Zadanie 5 - minimalne drzewo rozpinające (algorytm Kruskala)
def kruskal(G):
    parent = {v: v for v in G.nodes} #każdy wierzchołek jest osobnym drzewem

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    T = []
    edges = sorted(G.edges(data="weight"), key=lambda e: e[2]) #niemalejące wagi
    for u, v, wg in edges:
        ru, rv = find(u), find(v)
        if ru != rv: #krawędź łączy różne drzewa - nie tworzy cyklu
            parent[ru] = rv
            T.append((u, v, wg))
            if len(T) == len(G) - 1:
                break
    return T


def draw(G, T):
    pos = nx.spring_layout(G, seed=1)
    labels = nx.get_edge_attributes(G, "weight")
    tree = {(u, v) for u, v, _ in T} | {(v, u) for u, v, _ in T}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.set_title("Losowy graf z wagami")
    nx.draw(G, pos, ax=ax1, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12)
    nx.draw_networkx_edge_labels(G, pos, ax=ax1, edge_labels=labels)

    ax2.set_title(f"Minimalne drzewo rozpinające (waga: {sum(wg for _, _, wg in T)})")
    colors = ["blue" if e in tree else "lightgray" for e in G.edges]
    widths = [3 if e in tree else 1 for e in G.edges]
    nx.draw(G, pos, ax=ax2, with_labels=True, node_color="lightblue", node_size=800, edge_color=colors, width=widths, font_size=12)
    nx.draw_networkx_edge_labels(G, pos, ax=ax2, edge_labels=labels)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: weighted.py <nodes> <edges (int) | probability (float)> [start node]")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        if '.' in sys.argv[2]:
            MP = float(sys.argv[2])
        else:
            MP = int(sys.argv[2])
        START = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    except ValueError:
        print("Input values must be an integer, integer/float and optionally an integer")
        sys.exit(1)

    try:
        G = connected_weighted_graph(N, MP)
    except ValueError as e:
        print(e)
        sys.exit(1)

    if START not in G.nodes:
        print(f"Start node must be in range [1, {len(G)}]!")
        sys.exit(1)

    print("=== Zadanie 1 ===")
    print("Krawedzie (u, v, waga):")
    for u, v, wg in sorted(G.edges(data="weight")):
        print(f"{u} - {v}: {wg}")

    w = weight_matrix(G)

    print("\n=== Zadanie 2 ===")
    print(f"START: s = {START}")
    ds, ps = dijkstra(G, w, START)
    width = len(str(len(G)))
    for v in sorted(G.nodes):
        path = " - ".join(str(x) for x in get_path(ps, v))
        print(f"d({v})".ljust(width+3) + f" = {ds[v]}".ljust(6) + f"==> [{path}]")

    print("\n=== Zadanie 3 ===")
    print("Macierz odleglosci:")
    D = distance_matrix(G, w)
    cell = len(str(max(max(row) for row in D))) + 1
    for row in D:
        print("".join(str(x).rjust(cell) for x in row))

    print("\n=== Zadanie 4 ===")
    print(f"{'Wierzcholek':>11} | {'Suma odleglosci':>15} | {'Odleglosc od najdalszego':>24}")
    print("-"*12 + "+" + "-"*17 + "+" + "-"*25)
    for v, row in zip(sorted(G.nodes), D):
        print(f"{v:>11} | {sum(row):>15} | {max(row):>24}")

    (c, csum), (cm, cmax) = centers(D)
    print(f"\nCentrum = {c} (suma odleglosci: {csum})")
    print(f"Centrum minimax = {cm} (odleglosc od najdalszego: {cmax})")

    T = kruskal(G)
    print("\n=== Zadanie 5 ===")
    print("Minimalne drzewo rozpinajace (u, v, waga):")
    for u, v, wg in T:
        print(f"{u} - {v}: {wg}")
    print(f"Suma wag: {sum(wg for _, _, wg in T)}")

    draw(G, T)
