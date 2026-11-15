import matplotlib.pyplot as plt
import networkx as nx
import sys

from digraph import digraph_from_args, random_digraph, draw_digraph

#Zadanie 2 - algorytm Kosaraju (alg. 1-3 z alg_4.pdf): silnie spójne składowe digrafu
sys.setrecursionlimit(10000) #DFS_visit i components_r są rekurencyjne, jak w pseudokodzie


def kosaraju(G):
    #zwraca comp[v] - numer silnie spójnej składowej wierzchołka v (numeracja od 1)
    d, f = {}, {}
    for v in G.nodes:
        d[v] = -1 #wierzchołek nieodwiedzony
        f[v] = -1
    t = 0

    def DFS_visit(v):
        nonlocal t #DFS_visit musi modyfikować wspólny licznik czasu t (uwaga w alg_4.pdf)
        t += 1
        d[v] = t
        for u in sorted(G.successors(v)): #przejście po łuku (v, u)
            if d[u] == -1:
                DFS_visit(u)
        t += 1
        f[v] = t #czas przetworzenia

    for v in sorted(G.nodes):
        if d[v] == -1:
            DFS_visit(v)

    #transpozycja G - zwroty wszystkich łuków odwrócone
    GT = nx.DiGraph()
    GT.add_nodes_from(G.nodes)
    GT.add_edges_from((v, u) for u, v in G.edges)

    comp = {v: -1 for v in GT.nodes} #wszystkie wierzchołki nieodwiedzone

    def components_r(nr, v):
        for u in sorted(GT.successors(v)):
            if comp[u] == -1:
                comp[u] = nr
                components_r(nr, u)

    nr = 0
    for v in sorted(GT.nodes, key=lambda v: f[v], reverse=True): #malejące czasy przetworzenia f[v]
        if comp[v] == -1:
            nr += 1
            comp[v] = nr
            components_r(nr, v)
    return comp


def scc_list(comp):
    #lista składowych: element k-1 to posortowane wierzchołki składowej nr k
    groups = {}
    for v, nr in comp.items():
        groups.setdefault(nr, []).append(v)
    return [sorted(groups[nr]) for nr in sorted(groups)]

def is_strongly_connected(G):
    return len(G) > 0 and len(scc_list(kosaraju(G))) == 1

def random_strongly_connected(n, p, tries=100):
    #losuje G(n,p) aż Kosaraju zwróci jedną składową; po nieudanych próbach rzuca ValueError
    for _ in range(tries):
        G = random_digraph(n, p)
        if is_strongly_connected(G):
            return G
    raise ValueError(f"Could not draw a strongly connected digraph in {tries} tries - try higher probability.")


def print_components(comp):
    S = scc_list(comp)
    for nr, vs in enumerate(S, start=1):
        print(f"Skladowa {nr}: " + " ".join(map(str, vs)))
    print("Digraf jest silnie spojny" if len(S) == 1 else f"Digraf nie jest silnie spojny (liczba skladowych: {len(S)})")

def component_colors(G, comp):
    #kolor wierzchołka wg numeru składowej (do rysowania)
    cmap = plt.get_cmap("tab20")
    return [cmap((comp[v]-1) % 20) for v in G.nodes]


USAGE = """Usage:
  kosaraju.py <adj-l | adj-m | inc-m> <file>   strongly connected components of digraph from file
  kosaraju.py rand <n> <p>                     strongly connected components of random digraph G(n,p)"""

if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        res = digraph_from_args(args)
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    if res is None or res[2] != len(args):
        print(USAGE)
        sys.exit(1)
    G, title, _ = res

    comp = kosaraju(G)
    print_components(comp)
    draw_digraph(G, f"{title} - silnie spojne skladowe", node_color=component_colors(G, comp))
