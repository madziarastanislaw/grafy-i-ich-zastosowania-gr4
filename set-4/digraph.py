import matplotlib.pyplot as plt
import networkx as nx
import random
import re
import sys

#Zadanie 1 - kodowanie digrafów (lista sąsiedztwa, macierz sąsiedztwa, macierz incydencji) i losowanie G(n,p)
#Digraf przechowywany jako nx.DiGraph o wierzchołkach 1..n; łuk (u, v) = krawędź skierowana u -> v

FORMATS = ("adj-l", "adj-m", "inc-m")
INT_RE = re.compile(r"-?\d+")                 #liczba całkowita, np. 12
FLOAT_RE = re.compile(r"-?(\d+\.\d*|\.\d+)")  #ułamek dziesiętny, np. 0.3, .5, 1.


def parse_int(s, where=""):
    if not INT_RE.fullmatch(s):
        raise ValueError(f"{where}'{s}' is not an integer!")
    return int(s)

def parse_prob(s):
    if not FLOAT_RE.fullmatch(s):
        raise ValueError(f"'{s}' is not a decimal number (probability)!")
    return float(s)


def make_digraph(n, arcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(1, n+1))
    G.add_edges_from(arcs)
    return G


#---------- wczytywanie z pliku ----------

def read_rows(path):
    #wiersze pliku podzielone na tokeny; puste linie są pomijane
    with open(path, encoding="utf-8") as f:
        rows = [line.split() for line in f]
    rows = [r for r in rows if r]
    if not rows:
        raise ValueError("Input file is empty!")
    return rows

def from_adj_list(rows):
    #wiersz i: "i. v1 v2 ..." - wierzchołki, do których prowadzą łuki z i (następniki)
    n = len(rows)
    arcs = []
    for i, row in enumerate(rows, start=1):
        if row[0] != f"{i}.":
            raise ValueError(f"Line {i}: expected row label '{i}.', got '{row[0]}'!")
        nbrs = [parse_int(x, f"Line {i}: ") for x in row[1:]]
        for j in nbrs:
            if not 1 <= j <= n:
                raise ValueError(f"Line {i}: vertex {j} out of range [1, {n}]!")
            if j == i:
                raise ValueError(f"Line {i}: loop {i} -> {i} is not allowed!")
        if len(set(nbrs)) != len(nbrs):
            raise ValueError(f"Line {i}: repeated vertex (multiple arcs are not allowed)!")
        arcs += [(i, j) for j in nbrs]
    return make_digraph(n, arcs)

def from_adj_matrix(rows):
    #macierz n x n z 0/1; A[i][j] = 1 <=> łuk i -> j (macierz nie musi być symetryczna)
    n = len(rows)
    arcs = []
    for i, row in enumerate(rows, start=1):
        if len(row) != n:
            raise ValueError(f"Line {i}: expected {n} values (square matrix), got {len(row)}!")
        for j, x in enumerate(row, start=1):
            a = parse_int(x, f"Line {i}, column {j}: ")
            if a not in (0, 1):
                raise ValueError(f"Line {i}, column {j}: value must be 0 or 1, got {a}!")
            if a == 1 and i == j:
                raise ValueError(f"Line {i}, column {j}: diagonal must be 0 (loops are not allowed)!")
            if a == 1:
                arcs.append((i, j))
    return make_digraph(n, arcs)

def from_inc_matrix(rows):
    #macierz n x m; kolumna = łuk: -1 w wierszu początku, 1 w wierszu końca, reszta 0
    #opcjonalny ostatni wiersz "w: w1 ... wm" - waga łuku z danej kolumny (wagi mogą być ujemne lub 0,
    #więc nie da się ich wpisać w samą macierz, gdzie -1/1 oznacza kierunek)
    weight_row = None
    if rows[-1][0] == "w:":
        weight_row, rows = rows[-1][1:], rows[:-1]
        if not rows:
            raise ValueError("Incidence matrix is missing - only weight row given!")
    n, m = len(rows), len(rows[0])
    M = []
    for i, row in enumerate(rows, start=1):
        if len(row) != m:
            raise ValueError(f"Line {i}: expected {m} values (same as line 1), got {len(row)}!")
        M.append([parse_int(x, f"Line {i}, column {k}: ") for k, x in enumerate(row, start=1)])
        for k, x in enumerate(M[-1], start=1):
            if x not in (-1, 0, 1):
                raise ValueError(f"Line {i}, column {k}: value must be -1, 0 or 1, got {x}!")

    arcs = []
    for k in range(m):
        col = [M[i][k] for i in range(n)]
        tails = [i+1 for i, x in enumerate(col) if x == -1]
        heads = [i+1 for i, x in enumerate(col) if x == 1]
        if len(tails) != 1 or len(heads) != 1:
            raise ValueError(f"Column {k+1}: must contain exactly one -1 (start) and one 1 (end)!")
        arc = (tails[0], heads[0])
        if arc in arcs:
            raise ValueError(f"Column {k+1}: arc {arc[0]} -> {arc[1]} repeated (multiple arcs are not allowed)!")
        arcs.append(arc)
    G = make_digraph(n, arcs)

    if weight_row is not None:
        if len(weight_row) != m:
            raise ValueError(f"Weight row: expected {m} values (one per column), got {len(weight_row)}!")
        for k, ((u, v), x) in enumerate(zip(arcs, weight_row), start=1):
            G[u][v]["weight"] = parse_int(x, f"Weight row, column {k}: ")
    return G

def read_digraph(path, fmt):
    readers = {"adj-l": from_adj_list, "adj-m": from_adj_matrix, "inc-m": from_inc_matrix}
    return readers[fmt](read_rows(path))


#---------- losowanie G(n,p) ----------

def random_digraph(n, p):
    #każda uporządkowana para (i, j), i != j, niezależnie z prawdopodobieństwem p daje łuk i -> j
    #(łuki i -> j oraz j -> i losowane osobno, więc mogą wystąpić oba)
    if n < 1:
        raise ValueError("Number of nodes must be at least 1!")
    if p < 0 or p > 1:
        raise ValueError("Probability must be in range [0, 1]!")
    arcs = [(i, j) for i in range(1, n+1) for j in range(1, n+1) if i != j and random.random() < p]
    return make_digraph(n, arcs)


#---------- kodowanie (konwersja na 3 reprezentacje) ----------

def to_adj_list(G):
    return [sorted(G.successors(v)) for v in sorted(G.nodes)]

def to_adj_matrix(G):
    nodes = sorted(G.nodes)
    return [[1 if G.has_edge(u, v) else 0 for v in nodes] for u in nodes]

def to_inc_matrix(G):
    #kolumny uporządkowane wg początku, potem końca łuku (jak w input_4.pdf)
    arcs = sorted(G.edges)
    M = [[0]*len(arcs) for _ in G.nodes]
    for k, (u, v) in enumerate(arcs):
        M[u-1][k] = -1
        M[v-1][k] = 1
    return M

def is_weighted(G):
    return G.number_of_edges() > 0 and all("weight" in d for _, _, d in G.edges(data=True))

def inc_weights(G):
    #wagi łuków w kolejności kolumn macierzy incydencji (None dla digrafu bez wag)
    return [G[u][v]["weight"] for u, v in sorted(G.edges)] if is_weighted(G) else None

#formaty wyjścia są takie same jak formaty plików wejściowych (wynik można zapisać i wczytać ponownie)
def format_adj_list(L):
    return "\n".join(f"{i}." + "".join(f" {v}" for v in nbrs) for i, nbrs in enumerate(L, start=1))

def format_matrix(M):
    width = max((len(str(x)) for row in M for x in row), default=1)
    return "\n".join(" ".join(str(x).rjust(width) for x in row) for row in M)

def format_inc_matrix(G):
    #macierz incydencji; dla digrafu z wagami dodatkowy wiersz "w:" (wiersze macierzy wcięte, żeby kolumny się zgadzały)
    M, W = to_inc_matrix(G), inc_weights(G)
    if W is None:
        return format_matrix(M)
    width = max(len(str(x)) for x in [v for row in M for v in row] + W)
    rows = ["   " + " ".join(str(x).rjust(width) for x in row) for row in M]
    rows.append("w: " + " ".join(str(x).rjust(width) for x in W))
    return "\n".join(rows)


def print_digraph(G):
    print(f"Wierzcholki: {len(G)}, luki: {G.number_of_edges()}")
    print("\n--- Lista sasiedztwa ---")
    print(format_adj_list(to_adj_list(G)))
    print("\n--- Macierz sasiedztwa ---")
    print(format_matrix(to_adj_matrix(G)))
    print("\n--- Macierz incydencji ---")
    print(format_inc_matrix(G) if G.number_of_edges() else "(brak lukow)")


def draw_digraph(G, title="Digraf", ax=None, node_color="lightblue"):
    #bez ax - osobne okno; z ax - rysuje na podanym wykresie (kilka digrafów obok siebie)
    show = ax is None
    if show:
        _, ax = plt.subplots(figsize=(7, 6))
    pos = nx.circular_layout(G)
    style = "arc3,rad=0.1" #łuk zakrzywiony - widać oba kierunki u <-> v
    nx.draw_networkx(G, pos, ax=ax, node_color=node_color, node_size=800, font_size=12, edge_color="gray",
                     arrows=True, arrowsize=20, connectionstyle=style)
    if is_weighted(G):
        nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=nx.get_edge_attributes(G, "weight"),
                                     connectionstyle=style, font_size=10)
    ax.set_title(title)
    ax.axis("off")
    if show:
        plt.show()


def digraph_from_args(args):
    #wspólna obsługa CLI: "<adj-l|adj-m|inc-m> <plik>" lub "rand <n> <p>"; zwraca (G, opis, liczba zużytych argumentów)
    #rzuca ValueError/OSError przy błędnych danych, None gdy argumenty nie pasują do żadnego trybu
    if len(args) >= 2 and args[0] in FORMATS:
        return read_digraph(args[1], args[0]), f"Digraf z pliku {args[1]} ({args[0]})", 2
    if len(args) >= 3 and args[0] == "rand":
        return random_digraph(parse_int(args[1]), parse_prob(args[2])), f"Losowy digraf G({args[1]}, {args[2]})", 3
    return None


USAGE = """Usage:
  digraph.py <adj-l | adj-m | inc-m> <file>   read digraph from file in given representation
  digraph.py rand <n> <p>                     random digraph G(n,p), n - integer, p - decimal number"""

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

    print_digraph(G)
    draw_digraph(G, title)
