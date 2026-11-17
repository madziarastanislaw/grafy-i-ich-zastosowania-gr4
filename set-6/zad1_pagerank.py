"""Zestaw 6, zadanie 1: PageRank dla digrafu.

Metoda (a): bladzenie przypadkowe z teleportacja (PageRank = czestosc odwiedzin).
Metoda (b): iteracja wektora obsadzen p_{t+1} = p_t P.
Obie metody pracuja na tym samym grafie.

Uruchomienie (wszystkie opcje sa opcjonalne, domyslne wartosci z bloku KONFIGURACJA):
    python zad1_pagerank.py
    python zad1_pagerank.py --zrodlo plik --plik moj_graf.txt
    python zad1_pagerank.py --zrodlo losowy --n 20 --max-wyjscie 4 --ziarno 7
    python zad1_pagerank.py --krokow 2000000 --d 0.15
"""

import argparse
import random

# ============================== KONFIGURACJA ==============================
# Tu zmieniamy dane wejsciowe i parametry (mozna tez nadpisac z linii polecen).

ZRODLO_GRAFU = "plik"          # "plik" - wczytaj liste sasiedztwa, "losowy" - wylosuj digraf
PLIK_GRAFU = "graf_przyklad.txt"

LOSOWY_N = 12                  # liczba wierzcholkow grafu losowego
LOSOWY_MAX_WYJSCIE = 4         # maks. stopien wyjsciowy w grafie losowym (min. 1)
LOSOWY_PETLE = False           # czy dopuszczac petle (krawedz v -> v)

D = 0.15                       # prawdopodobienstwo teleportacji
LICZBA_KROKOW = 1_000_000      # N krokow bladzenia przypadkowego (metoda a)
EPS = 1e-10                    # prog zbieznosci metody potegowej (metoda b)
MAX_ITERACJI = 1000            # zabezpieczenie, gdyby wektor nie zbiegl
ZIARNO = None                  # ziarno generatora losowego (None = losowe, liczba = powtarzalne)
# ==========================================================================


def wczytaj_graf(sciezka):
    """Wczytuje liste sasiedztwa w formacie 'A : E, F, I' (jedna linia = jeden wierzcholek).

    Puste linie i linie zaczynajace sie od '#' sa pomijane. Zwraca slownik
    {wierzcholek: [sasiedzi]} z zachowaniem kolejnosci z pliku.
    """
    graf = {}
    with open(sciezka, encoding="utf-8") as f:
        for nr, linia in enumerate(f, 1):
            linia = linia.strip()
            if not linia or linia.startswith("#"):
                continue
            if ":" not in linia:
                raise ValueError(f"{sciezka}:{nr}: brak ':' w linii '{linia}'")
            wierzcholek, reszta = linia.split(":", 1)
            wierzcholek = wierzcholek.strip()
            if not wierzcholek:
                raise ValueError(f"{sciezka}:{nr}: pusta nazwa wierzcholka")
            if wierzcholek in graf:
                raise ValueError(f"{sciezka}:{nr}: wierzcholek '{wierzcholek}' zdefiniowany dwa razy")
            sasiedzi = [s.strip() for s in reszta.replace(";", ",").split(",") if s.strip()]
            # duplikaty krawedzi usuwamy (graf prosty), zachowujac kolejnosc
            graf[wierzcholek] = list(dict.fromkeys(sasiedzi))
    return graf


def losuj_graf(n, max_wyjscie, petle=False):
    """Losuje digraf o n wierzcholkach; z kazdego wierzcholka wychodzi >= 1 krawedz."""
    if n < 1:
        raise ValueError("n musi byc >= 1")
    if max_wyjscie < 1:
        raise ValueError("max_wyjscie musi byc >= 1")
    nazwy = [nazwa_wierzcholka(i) for i in range(n)]
    graf = {}
    for v in nazwy:
        kandydaci = nazwy if petle else [u for u in nazwy if u != v]
        if not kandydaci:
            raise ValueError("dla n = 1 trzeba dopuscic petle (LOSOWY_PETLE = True)")
        k = random.randint(1, min(max_wyjscie, len(kandydaci)))
        graf[v] = random.sample(kandydaci, k)
    return graf


def nazwa_wierzcholka(i):
    """0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, ..."""
    nazwa = ""
    i += 1
    while i > 0:
        i, r = divmod(i - 1, 26)
        nazwa = chr(ord("A") + r) + nazwa
    return nazwa


def sprawdz_graf(graf):
    """Kazdy wierzcholek musi miec krawedz wychodzaca, a krawedzie musza prowadzic do znanych wierzcholkow."""
    if not graf:
        raise ValueError("pusty graf")
    for v, sasiedzi in graf.items():
        if not sasiedzi:
            raise ValueError(f"wierzcholek '{v}' nie ma krawedzi wychodzacych (wymagane >= 1)")
        for u in sasiedzi:
            if u not in graf:
                raise ValueError(f"krawedz {v} -> {u}: wierzcholek '{u}' nie ma wlasnej linii w grafie")


def pagerank_bladzenie(graf, d, liczba_krokow):
    """Metoda (a): bladzenie przypadkowe. Zwraca {wierzcholek: czestosc odwiedzin}."""
    wierzcholki = list(graf)
    odwiedziny = {v: 0 for v in wierzcholki}
    v = random.choice(wierzcholki)
    for _ in range(liczba_krokow):
        if random.random() < d:
            v = random.choice(wierzcholki)      # teleportacja
        else:
            v = random.choice(graf[v])          # losowy sasiad
        odwiedziny[v] += 1
    return {v: odwiedziny[v] / liczba_krokow for v in wierzcholki}


def pagerank_iteracja(graf, d, eps, max_iter):
    """Metoda (b): iteracja wektora obsadzen p_{t+1} = p_t P,
    P_ij = (1-d) A_ij / d_i + d/n.

    Zwraca (wynik, liczba_iteracji, zbiegl). Jesli wektor nie zbiegl w max_iter
    krokach, wynikiem jest srednia z kolejnych wektorow (jak w tresci zadania).
    """
    wierzcholki = list(graf)
    n = len(wierzcholki)
    idx = {v: i for i, v in enumerate(wierzcholki)}
    wyjscia = [[idx[u] for u in graf[v]] for v in wierzcholki]

    p = [1.0 / n] * n
    suma = [0.0] * n
    for t in range(1, max_iter + 1):
        nowy = [d / n] * n          # skladnik teleportacji (sum(p) = 1)
        for i in range(n):
            udzial = (1 - d) * p[i] / len(wyjscia[i])
            for j in wyjscia[i]:
                nowy[j] += udzial
        roznica = max(abs(nowy[i] - p[i]) for i in range(n))
        p = nowy
        for i in range(n):
            suma[i] += p[i]
        if roznica < eps:
            return {v: p[idx[v]] for v in wierzcholki}, t, True
    return {v: suma[idx[v]] / max_iter for v in wierzcholki}, max_iter, False


def wypisz_ranking(wynik, tytul):
    print(tytul)
    for v, wartosc in sorted(wynik.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{v} ==> PageRank = {wartosc:.6f}")
    print()


def porownaj(wynik_a, wynik_b):
    """Porownanie obu metod: maks. i srednia roznica oraz zgodnosc kolejnosci rankingu."""
    roznice = [abs(wynik_a[v] - wynik_b[v]) for v in wynik_a]
    rank_a = [v for v, _ in sorted(wynik_a.items(), key=lambda kv: (-kv[1], kv[0]))]
    rank_b = [v for v, _ in sorted(wynik_b.items(), key=lambda kv: (-kv[1], kv[0]))]
    print("Porownanie metod (a) i (b):")
    print(f"  maksymalna roznica wartosci: {max(roznice):.6f}")
    print(f"  srednia roznica wartosci:    {sum(roznice) / len(roznice):.6f}")
    print(f"  ta sama kolejnosc rankingu:  {'tak' if rank_a == rank_b else 'nie'}")
    if rank_a != rank_b:
        print(f"  ranking (a): {' '.join(rank_a)}")
        print(f"  ranking (b): {' '.join(rank_b)}")


def parsuj_argumenty():
    ap = argparse.ArgumentParser(description="PageRank: bladzenie przypadkowe vs iteracja wektora obsadzen")
    ap.add_argument("--zrodlo", choices=["plik", "losowy"], default=ZRODLO_GRAFU)
    ap.add_argument("--plik", default=PLIK_GRAFU, help="plik z lista sasiedztwa")
    ap.add_argument("--n", type=int, default=LOSOWY_N, help="liczba wierzcholkow (graf losowy)")
    ap.add_argument("--max-wyjscie", type=int, default=LOSOWY_MAX_WYJSCIE,
                    help="maks. stopien wyjsciowy (graf losowy)")
    ap.add_argument("--petle", action="store_true", default=LOSOWY_PETLE,
                    help="dopusc petle w grafie losowym")
    ap.add_argument("--d", type=float, default=D, help="prawdopodobienstwo teleportacji")
    ap.add_argument("--krokow", type=int, default=LICZBA_KROKOW, help="liczba krokow bladzenia")
    ap.add_argument("--eps", type=float, default=EPS)
    ap.add_argument("--max-iter", type=int, default=MAX_ITERACJI)
    ap.add_argument("--ziarno", type=int, default=ZIARNO)
    return ap.parse_args()


def main():
    arg = parsuj_argumenty()
    if not 0 <= arg.d <= 1:
        raise SystemExit("d musi nalezec do przedzialu [0, 1]")
    if arg.krokow < 1:
        raise SystemExit("liczba krokow musi byc >= 1")
    if arg.ziarno is not None:
        random.seed(arg.ziarno)

    if arg.zrodlo == "plik":
        graf = wczytaj_graf(arg.plik)
    else:
        graf = losuj_graf(arg.n, arg.max_wyjscie, arg.petle)
    sprawdz_graf(graf)

    print("Graf (listy sasiedztwa):")
    for v, sasiedzi in graf.items():
        print(f"{v} : {', '.join(sasiedzi)}")
    print()

    wynik_a = pagerank_bladzenie(graf, arg.d, arg.krokow)
    wynik_b, iteracje, zbiegl = pagerank_iteracja(graf, arg.d, arg.eps, arg.max_iter)

    wypisz_ranking(wynik_a, f"(a) Efekt N = {arg.krokow} krokow bladzenia przypadkowego z teleportacja:")
    if zbiegl:
        opis = f"zbieznosc uzyskano po {iteracje} iteracjach"
    else:
        opis = f"brak zbieznosci po {iteracje} iteracjach - wynik to srednia wektorow"
    wypisz_ranking(wynik_b, f"(b) Efekt metody iteracji wektora obsadzen ({opis}):")
    porownaj(wynik_a, wynik_b)


if __name__ == "__main__":
    main()
