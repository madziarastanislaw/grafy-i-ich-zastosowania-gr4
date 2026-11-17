import matplotlib.pyplot as plt
import random
import sys
import os

from digraph import digraph_from_args, parse_int, print_digraph, format_inc_matrix, draw_digraph, is_weighted
from kosaraju import kosaraju, scc_list, print_components, component_colors, random_strongly_connected

#importy z poprzednich zestawów
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "set-3"))
from weighted import dijkstra, get_path #set-3, zad. 2 - algorytm Dijkstry (działa też dla digrafów: G[u] = następniki u)

INF = float("inf")
WMIN, WMAX = -5, 10 #przedział wag łuków (zad. 3)


#Zadanie 3 - losowy silnie spójny digraf z wagami, algorytm Bellmana-Forda (alg. 4 z alg_4.pdf)
def weight_matrix(G):
    #w[u][v] - waga łuku u -> v, INF gdy łuku brak; indeksy 1..n, indeks 0 zarezerwowany na wierzchołek s Johnsona
    n = len(G)
    w = [[INF]*(n+1) for _ in range(n+1)]
    for u, v, wg in G.edges(data="weight"):
        w[u][v] = wg
    return w

def bellman_ford(G, w, s):
    #zwraca (True, ds, ps) lub (False, ds, ps) gdy z s osiągalny jest cykl o ujemnej wadze
    ds, ps = {}, {}
    for v in G.nodes: #init(G, s)
        ds[v] = INF
        ps[v] = None
    ds[s] = 0

    def relax(u, v):
        if ds[v] > ds[u] + w[u][v]:
            ds[v] = ds[u] + w[u][v]
            ps[v] = u

    for _ in range(len(G)-1): #n-1 iteracji
        for u, v in G.edges:
            relax(u, v)
    for u, v in G.edges:
        if ds[v] > ds[u] + w[u][v]:
            return False, ds, ps
    return True, ds, ps


#Zadanie 4 - algorytm Johnsona (alg. 5-6 z alg_4.pdf)
def add_s(G, w):
    #G' = G z dodatkowym wierzchołkiem s = 0 i łukami s -> v o wadze 0; zwraca (G', w', s)
    G1 = G.copy()
    w1 = [row[:] for row in w]
    s = 0
    G1.add_node(s)
    for v in G.nodes:
        G1.add_edge(s, v)
        w1[s][v] = 0
    return G1, w1, s

def has_negative_cycle(G):
    G1, w1, s = add_s(G, weight_matrix(G)) #z s osiągalne są wszystkie wierzchołki, więc wykryty zostanie każdy cykl
    return not bellman_ford(G1, w1, s)[0]

def johnson(G, w):
    #zwraca macierz odległości D (wiersze/kolumny w kolejności wierzchołków 1..n)
    G1, w1, s = add_s(G, w)
    ok, ds, _ = bellman_ford(G1, w1, s)
    if not ok:
        raise ValueError("Digraph contains a negative cycle!")
    h = ds #h[v] = ds[v] z Bellmana-Forda

    n = len(G)
    wb = [[INF]*(n+1) for _ in range(n+1)] #przeskalowane, nieujemne wagi
    for u, v in G1.edges:
        wb[u][v] = w1[u][v] + h[u] - h[v]

    nodes = sorted(G.nodes)
    D = []
    for u in nodes:
        du, _ = dijkstra(G, wb, u) #najkrótsze ścieżki z u dla wag wb
        D.append([du[v] - h[u] + h[v] for v in nodes])
    return D


def random_weights(G, tries=100):
    #losuje wagi z [WMIN, WMAX]; jeśli powstał cykl o ujemnej wadze - losuje ponownie (dopuszczone w input_4.pdf)
    for _ in range(tries):
        for u, v in G.edges:
            G[u][v]["weight"] = random.randint(WMIN, WMAX)
        if not has_negative_cycle(G):
            return
    raise ValueError(f"Could not draw weights from [{WMIN}, {WMAX}] without a negative cycle in {tries} tries - try lower probability.")


def format_labeled_matrix(D, nodes):
    #macierz z etykietami wierszy (od) i kolumn (do)
    cell = max(len(str(x)) for row in D for x in row + [nodes[-1]]) + 1
    lab = len(str(nodes[-1]))
    lines = [" "*lab + " |" + "".join(str(v).rjust(cell) for v in nodes),
             "-"*lab + "-+" + "-"*(cell*len(nodes))]
    for v, row in zip(nodes, D):
        lines.append(str(v).rjust(lab) + " |" + "".join(str(x).rjust(cell) for x in row))
    return "\n".join(lines)


USAGE = """Usage:
  johnson.py rand <n> <p> [start]                    tasks 1-4 on random digraph G(n,p)
  johnson.py <adj-l | adj-m | inc-m> <file> [start]  tasks 1-4 on digraph from file
                                                     (inc-m with weight row 'w:' - its weights are used)
  start - start vertex for Bellman-Ford (default 1)"""

if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        res = digraph_from_args(args)
        if res is None or len(args) - res[2] > 1:
            print(USAGE)
            sys.exit(1)
        G, title, used = res
        START = parse_int(args[used]) if len(args) > used else 1
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    if START not in G.nodes:
        print(f"Error: start vertex must be in range [1, {len(G)}]!")
        sys.exit(1)

    print("=== Zadanie 1 ===")
    print(title)
    print_digraph(G)

    print("\n=== Zadanie 2 ===")
    comp = kosaraju(G)
    print_components(comp)

    #rysunek: digraf z zad. 1-2 (kolory = składowe) obok digrafu z wagami z zad. 3-4
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    draw_digraph(G, "Zad. 1-2: silnie spojne skladowe", ax=ax1, node_color=component_colors(G, comp))

    print("\n=== Zadanie 3 ===")
    try:
        if args[0] == "rand":
            n, p = len(G), float(args[2])
            if len(scc_list(comp)) != 1:
                G = random_strongly_connected(n, p) #losujemy do skutku (Kosaraju sprawdza silną spójność)
                print("Wylosowano nowy, silnie spojny digraf G(n,p)")
            else:
                print("Digraf z zad. 1 jest silnie spojny - uzywamy go dalej")
            random_weights(G)
            print(f"Wagi lukow wylosowane z przedzialu [{WMIN}, {WMAX}] (bez cyklu o ujemnej wadze)")
        else:
            if len(scc_list(comp)) != 1:
                print("Digraf z pliku nie jest silnie spojny - zadania 3-4 wymagaja digrafu silnie spojnego")
                sys.exit(1)
            if is_weighted(G):
                print("Wagi lukow wczytane z pliku")
                if has_negative_cycle(G):
                    raise ValueError("Digraph from file contains a negative cycle!")
            else:
                random_weights(G)
                print(f"Wagi lukow wylosowane z przedzialu [{WMIN}, {WMAX}] (bez cyklu o ujemnej wadze)")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Macierz incydencji z wagami:")
    print(format_inc_matrix(G))

    w = weight_matrix(G)
    ok, ds, ps = bellman_ford(G, w, START)
    print(f"\nBellman-Ford, START: s = {START}")
    width = len(str(len(G)))
    for v in sorted(G.nodes):
        path = " - ".join(str(x) for x in get_path(ps, v))
        print(f"d({v})".ljust(width+3) + f" = {ds[v]}".ljust(6) + f"==> [{path}]")

    print("\n=== Zadanie 4 ===")
    print("Macierz odleglosci (algorytm Johnsona), wiersz - od, kolumna - do:")
    D = johnson(G, w)
    print(format_labeled_matrix(D, sorted(G.nodes)))

    draw_digraph(G, "Zad. 3-4: silnie spojny digraf z wagami", ax=ax2)
    plt.show()
