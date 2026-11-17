from collections import deque
import os
import random
import sys
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "set-3"))
from connected import parse_int
from weighted import INF, get_path


def generate_network(n):
    counts = [random.randint(2, n) for _ in range(n)]
    alpha = [chr(c) for c in range(97, 123) if chr(c) not in ("s", "t")]
    names = alpha[:sum(counts)] if sum(counts) <= len(alpha) else [f"v{i}" for i in range(1, sum(counts) + 1)]
    layers, idx = [["s"]], 0
    for c in counts:
        layers.append(names[idx:idx + c])
        idx += c
    layers.append(["t"])
    nodes = [v for layer in layers for v in layer]
    edges = set()

    for i in range(len(layers) - 1):
        a, b = layers[i], layers[i + 1]
        covered = set()
        for u in a:
            v = random.choice(b)
            edges.add((u, v))
            covered.add(v)
        for v in b:
            if v not in covered:
                edges.add((random.choice(a), v))

    pool = [(u, v) for u in nodes for v in nodes if u != v and v != "s" and u != "t" and (u, v) not in edges]
    edges.update(random.sample(pool, 2 * n))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for u, v in edges:
        G.add_edge(u, v, capacity=random.randint(1, 10))
    return G, layers


def cf(G, f, u, v):
    if G.has_edge(u, v) and G.has_edge(v, u):
        return (G[u][v]["capacity"] - f[(u, v)]) + f[(v, u)]
    if G.has_edge(u, v):
        return G[u][v]["capacity"] - f[(u, v)]
    if G.has_edge(v, u):
        return f[(v, u)]
    return 0


def bfs(G, f, s, t):
    ds = {}
    ps = {}

    def init(G, s):
        for v in G.nodes:
            ds[v] = INF
            ps[v] = None
        ds[s] = 0

    init(G, s)
    Q = deque([s])
    while Q:
        v = Q.popleft()
        neighbors = list(G.successors(v)) + [x for x in G.predecessors(v) if not G.has_edge(v, x)]
        for u in neighbors:
            if ds[u] == INF and cf(G, f, v, u) > 0:
                ds[u] = ds[v] + 1
                ps[u] = v
                Q.append(u)
                if u == t:
                    nodes = get_path(ps, t)
                    return list(zip(nodes, nodes[1:]))
    return None


def ford_fulkerson(G, s="s", t="t"):
    f = {e: 0 for e in G.edges}
    while (p := bfs(G, f, s, t)) is not None:
        cf_p = min(cf(G, f, u, v) for u, v in p)
        for u, v in p:
            if G.has_edge(v, u) and f[(v, u)] > 0:
                cancel = min(cf_p, f[(v, u)])
                f[(v, u)] -= cancel
                if cf_p > cancel and G.has_edge(u, v):
                    f[(u, v)] += cf_p - cancel
            elif G.has_edge(u, v):
                f[(u, v)] += cf_p
    max_flow = sum(f[(s, v)] for v in G.successors(s)) - sum(f[(v, s)] for v in G.predecessors(s))
    return f, max_flow


def draw(G, layers, f, max_flow):
    pos = {}
    for i, layer in enumerate(layers):
        k = len(layer)
        ys = [0.0] if k == 1 else np.linspace(k - 1, -(k - 1), k) * 0.7
        shift = 0.15 if i % 2 else -0.15
        for j, v in enumerate(layer):
            dx = (0.12 if j % 2 == 0 else -0.12) if k >= 3 else 0.0
            pos[v] = (float(i) + dx, float(ys[j]) + (shift if k > 1 else 0.0))

    labels1 = nx.get_edge_attributes(G, "capacity")
    labels2 = {(u, v): f"{f[(u, v)]}/{d['capacity']}" for u, v, d in G.edges(data=True)}
    colors = ["blue" if f[e] > 0 else "lightgray" for e in G.edges]
    widths = [3 if f[e] > 0 else 1 for e in G.edges]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.set_title(f"Sieć przepływowa N ={len(layers) - 2}")
    nx.draw(G, pos, ax=ax1, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, connectionstyle="arc3,rad=0.1")
    nx.draw_networkx_edge_labels(G, pos, ax=ax1, edge_labels=labels1, label_pos=0.35, rotate=False)

    ax2.set_title(f"Maksymalny przepływ f_max= {max_flow}")
    nx.draw(G, pos, ax=ax2, with_labels=True, node_color="lightblue", node_size=800, edge_color=colors, width=widths, font_size=12, connectionstyle="arc3,rad=0.1")
    nx.draw_networkx_edge_labels(G, pos, ax=ax2, edge_labels=labels2, label_pos=0.35, rotate=False)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: flow.py <N>")
        sys.exit(1)

    try:
        N = parse_int(sys.argv[1])
        if N < 2:
            raise ValueError("N must be at least 2!")
    except ValueError as e:
        print(e)
        sys.exit(1)

    G, layers = generate_network(N)
    f, max_flow = ford_fulkerson(G)

    print("zad1")
    for i, layer in enumerate(layers):
        print(f"Warstwa {i}: {' '.join(layer)}")
    for u, v, d in G.edges(data=True):
        print(f"{u} -> {v}: {d['capacity']}")

    print("\nzad2")
    for u, v, d in G.edges(data=True):
        print(f"{u} -> {v}: {f[(u, v)]}/{d['capacity']}")
    print(f"|f_max| = {max_flow}")

    draw(G, layers, f, max_flow)