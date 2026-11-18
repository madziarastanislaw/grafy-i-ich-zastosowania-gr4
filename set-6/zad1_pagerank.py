import argparse
import os
import random
import sys

#importy z poprzednich zestawów
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "set-4"))
from digraph import digraph_from_args, draw_digraph, format_adj_list, to_adj_list #set-4, zad. 1 - kodowanie i losowanie digrafów

#Zadanie 1 - algorytm PageRank dla digrafu (input_6.pdf), dwie metody na tym samym digrafie:
#(a) błądzenie przypadkowe z teleportacją - PageRank = częstość odwiedzin,
#(b) iteracja wektora obsadzeń p(t+1) = p(t)P, P_ij = (1-d)A_ij/d_i + d/n
#Digraf wczytywany tak jak w set-4 (adj-l / adj-m / inc-m z pliku albo rand n p), wierzchołki 1..n

#wartości domyślne - każdą można nadpisać flagą z linii poleceń (python zad1_pagerank.py --help)
DOMYSLNE_WEJSCIE = ["adj-l", os.path.join(BASE, "demo_adj_l.txt")] #używane, gdy nie podano digrafu
D = 0.15                  #prawdopodobieństwo teleportacji
LICZBA_KROKOW = 1_000_000 #N kroków błądzenia przypadkowego (metoda a)
EPS = 1e-10               #próg zbieżności metody iteracyjnej (metoda b)
MAX_ITERACJI = 1000       #zabezpieczenie, gdyby wektor się nie ustabilizował
ZIARNO = None             #None = losowo, liczba całkowita = powtarzalne wyniki


USAGE = """Usage:
  zad1_pagerank.py [<adj-l | adj-m | inc-m> <file>] [options]   digraf z pliku w podanej reprezentacji
  zad1_pagerank.py [rand <n> <p>] [options]                      losowy digraf G(n,p) (wierzchołki bez łuków wychodzących dostają jeden losowy łuk)
  bez digrafu: przykład z input_6.pdf (demo_adj_l.txt)
  options: --d D  --krokow N  --eps EPS  --max-iter K  --ziarno S  --rysuj"""


def ensure_out_arcs(G):
    #PageRank wymaga co najmniej jednego łuku wychodzącego z każdego wierzchołka (input_6.pdf):
    #w losowym G(n,p) wierzchołkom bez następników dolosowujemy jeden łuk do innego wierzchołka
    if len(G) < 2 and G.number_of_edges() == 0:
        raise ValueError("Digraph with one node needs a loop - PageRank requires an arc out of every node!")
    for v in sorted(G.nodes):
        if G.out_degree(v) == 0:
            G.add_edge(v, random.choice([u for u in G.nodes if u != v]))

def check_out_arcs(G):
    #digraf z pliku nie jest zmieniany - brak łuku wychodzącego to błąd danych
    for v in sorted(G.nodes):
        if G.out_degree(v) == 0:
            raise ValueError(f"Node {v} has no outgoing arcs - PageRank requires at least one arc out of every node!")


def pagerank_random_walk(G, d, steps):
    #metoda (a): z prawdopodobieństwem d teleportacja do losowego wierzchołka, w przeciwnym razie krok po losowym łuku wychodzącym
    nodes = sorted(G.nodes)
    succ = {v: list(G.successors(v)) for v in nodes}
    visits = {v: 0 for v in nodes}
    v = random.choice(nodes) #wierzchołek startowy
    for _ in range(steps):
        if random.random() < d:
            v = random.choice(nodes) #teleportacja
        else:
            v = random.choice(succ[v]) #losowy następnik
        visits[v] += 1
    return {v: visits[v] / steps for v in nodes} #częstość odwiedzin = PageRank

def pagerank_power(G, d, eps, max_iter):
    #metoda (b): p(t+1) = p(t)P, P_ij = (1-d)A_ij/d_i + d/n, p(0) = (1/n, ..., 1/n)
    #zwraca (PageRank, liczba iteracji, czy zbiegło); bez zbieżności w max_iter krokach wynik = średnia kolejnych wektorów
    nodes = sorted(G.nodes)
    n = len(nodes)
    succ = {v: list(G.successors(v)) for v in nodes}
    p = {v: 1.0/n for v in nodes}
    total = {v: 0.0 for v in nodes} #suma kolejnych wektorów (do średniej, gdy brak zbieżności)
    for t in range(1, max_iter+1):
        new = {v: d/n for v in nodes} #składnik teleportacji (suma p = 1)
        for i in nodes:
            share = (1-d) * p[i] / len(succ[i]) #udział i dzielony równo między jego następniki
            for j in succ[i]:
                new[j] += share
        diff = max(abs(new[v] - p[v]) for v in nodes)
        p = new
        for v in nodes:
            total[v] += p[v]
        if diff < eps: #wektor się ustabilizował
            return p, t, True
    return {v: total[v]/max_iter for v in nodes}, max_iter, False


def ranking(pr):
    #wierzchołki od najważniejszego; przy remisie mniejszy numer wierzchołka
    return sorted(pr.items(), key=lambda kv: (-kv[1], kv[0]))

def print_ranking(title, pr):
    print(title)
    for v, x in ranking(pr):
        print(f"{v} ==> PageRank = {x:.6f}")
    print()

def compare(pr_a, pr_b):
    #porównanie metod: różnice wartości oraz zgodność kolejności rankingów
    diffs = [abs(pr_a[v] - pr_b[v]) for v in pr_a]
    order_a = [v for v, _ in ranking(pr_a)]
    order_b = [v for v, _ in ranking(pr_b)]
    print("Porownanie metod (a) i (b):")
    print(f"  maksymalna roznica wartosci: {max(diffs):.6f}")
    print(f"  srednia roznica wartosci:    {sum(diffs)/len(diffs):.6f}")
    print(f"  ta sama kolejnosc rankingu:  {'tak' if order_a == order_b else 'nie'}")
    if order_a != order_b:
        print(f"  ranking (a): {' '.join(map(str, order_a))}")
        print(f"  ranking (b): {' '.join(map(str, order_b))}")


def parse_args():
    #add_help=False, bo -h/--help obsługujemy sami (wypisujemy USAGE w tym samym formacie co przy błędzie)
    ap = argparse.ArgumentParser(usage=USAGE, add_help=False)
    ap.add_argument("digraf", nargs="*") #"<adj-l | adj-m | inc-m> <plik>" lub "rand <n> <p>", przekazywane do digraph_from_args
    ap.add_argument("--d", type=float, default=D)
    ap.add_argument("--krokow", type=int, default=LICZBA_KROKOW)
    ap.add_argument("--eps", type=float, default=EPS)
    ap.add_argument("--max-iter", type=int, default=MAX_ITERACJI)
    ap.add_argument("--ziarno", type=int, default=ZIARNO)
    ap.add_argument("--rysuj", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    return ap.parse_args()

def main():
    a = parse_args()
    if a.help:
        print(USAGE)
        return
    if not 0 <= a.d <= 1:
        print("Error: d must be in range [0, 1]!")
        sys.exit(1)
    if a.krokow < 1 or a.max_iter < 1 or a.eps <= 0:
        print("Error: --krokow and --max-iter must be >= 1 and --eps must be positive!")
        sys.exit(1)
    if a.ziarno is not None:
        random.seed(a.ziarno)

    #digraf: z linii poleceń albo domyślny przykład z input_6.pdf
    spec = a.digraf or DOMYSLNE_WEJSCIE
    try:
        res = digraph_from_args(spec)
        if res is None or res[2] != len(spec): #nierozpoznany tryb albo nadmiarowe argumenty
            print(USAGE)
            sys.exit(1)
        G, title, _ = res
        if spec[0] == "rand":
            ensure_out_arcs(G)
        else:
            check_out_arcs(G)
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"{title}: {len(G)} wierzcholkow, {G.number_of_edges()} lukow")
    print("--- Lista sasiedztwa ---")
    print(format_adj_list(to_adj_list(G)))
    print()

    #obie metody na tym samym digrafie
    pr_a = pagerank_random_walk(G, a.d, a.krokow)
    pr_b, iterations, converged = pagerank_power(G, a.d, a.eps, a.max_iter)

    print_ranking(f"(a) Efekt N = {a.krokow} krokow bladzenia przypadkowego z teleportacja (d = {a.d}):", pr_a)
    if converged:
        info = f"zbieznosc uzyskano po {iterations} iteracjach"
    else:
        info = f"brak zbieznosci po {iterations} iteracjach - wynik to srednia wektorow"
    print_ranking(f"(b) Efekt metody iteracji wektora obsadzen ({info}):", pr_b)
    compare(pr_a, pr_b)

    if a.rysuj:
        draw_digraph(G, title)


if __name__ == "__main__":
    main()
