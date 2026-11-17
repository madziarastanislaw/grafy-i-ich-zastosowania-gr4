"""Zestaw 6, zadanie 2: komiwojazer - symulowane wyzarzanie (Metropolis-Hastings + ruch 2-opt).

Uruchomienie (wszystkie opcje sa opcjonalne, domyslne wartosci z bloku KONFIGURACJA):
    python zad2_tsp.py
    python zad2_tsp.py --plik inne_punkty.txt --powtorzen 10 --max-it 100000
    python zad2_tsp.py --chlodzenie liniowe --ziarno 5 --bez-okna
"""

import argparse
import math
import random

# ============================== KONFIGURACJA ==============================
PLIK_PUNKTOW = "xqf131.dat.txt"   # plik: w kazdej linii "x y"

CHLODZENIE = "kwadratowe"         # "kwadratowe" | "liniowe" | "wykladnicze"
KROKI_CHLODZENIA = 100            # liczba poziomow temperatury (i = 100 ... 2 w pseudokodzie)
T_START = 10.0                    # temperatura poczatkowa (0.001 * 100^2 = 10)
T_KONIEC = 0.004                  # temperatura koncowa    (0.001 * 2^2   = 0.004)
MAX_IT = 50_000                   # iteracji na jeden poziom temperatury
POWTORZEN = 5                     # ile razy powtorzyc cala procedure
START_Z_NAJLEPSZEGO = True        # kolejne powtorzenia startuja od najlepszego dotad cyklu
ZIARNO = None                     # None = losowe, liczba = powtarzalne wyniki
PLIK_WYKRESU = "cykl_wynik.png"   # None = nie zapisuj
POKAZ_OKNO = True                 # czy otworzyc okno z wykresem
# ==========================================================================


def wczytaj_punkty(sciezka):
    """Wczytuje punkty z pliku: kazda niepusta linia to 'x y' (rozdzielone bialymi znakami)."""
    punkty = []
    with open(sciezka, encoding="utf-8") as f:
        for nr, linia in enumerate(f, 1):
            linia = linia.strip()
            if not linia or linia.startswith("#"):
                continue
            kolumny = linia.split()
            if len(kolumny) < 2:
                raise ValueError(f"{sciezka}:{nr}: oczekiwano dwoch wspolrzednych, jest '{linia}'")
            punkty.append((float(kolumny[0]), float(kolumny[1])))
    return punkty


def macierz_odleglosci(punkty):
    n = len(punkty)
    return [[math.hypot(punkty[i][0] - punkty[j][0], punkty[i][1] - punkty[j][1])
             for j in range(n)] for i in range(n)]


def dlugosc_cyklu(cykl, dist):
    return sum(dist[cykl[i]][cykl[(i + 1) % len(cykl)]] for i in range(len(cykl)))


def harmonogram_temperatur(rodzaj, kroki, t_start, t_koniec):
    """Zwraca liste temperatur od t_start do t_koniec (malejaco), 'kroki' poziomow."""
    if kroki < 2:
        return [t_start]
    if rodzaj == "liniowe":
        return [t_start + (t_koniec - t_start) * k / (kroki - 1) for k in range(kroki)]
    if rodzaj == "wykladnicze":
        q = (t_koniec / t_start) ** (1.0 / (kroki - 1))
        return [t_start * q ** k for k in range(kroki)]
    if rodzaj == "kwadratowe":
        # T proporcjonalne do i^2, gdzie i maleje liniowo; krance dokladnie t_start i t_koniec
        a, b = math.sqrt(t_start), math.sqrt(t_koniec)
        return [(a + (b - a) * k / (kroki - 1)) ** 2 for k in range(kroki)]
    raise ValueError(f"nieznany rodzaj chlodzenia: {rodzaj}")


def symulowane_wyzarzanie(cykl_start, dist, temperatury, max_it):
    """Algorytm 1 z alg_6.pdf. Ruch 2-opt: krawedzie (a,b), (c,d) -> (a,c), (b,d)
    przez odwrocenie fragmentu cyklu miedzy b a c.

    Roznica dlugosci liczona w O(1) (d(Pnew) - d(P) = nowe krawedzie - stare krawedzie);
    odwracanie fragmentu wykonujemy tylko przy akceptacji. Zwraca (najlepszy cykl,
    jego dlugosc, ostatni cykl).
    """
    cykl = list(cykl_start)
    n = len(cykl)
    dl = dlugosc_cyklu(cykl, dist)
    najlepszy, najlepsza_dl = list(cykl), dl
    if n < 4:
        return najlepszy, najlepsza_dl, cykl     # 2-opt nie ma sensu dla n < 4

    los = random.random
    losint = random.randrange
    for T in temperatury:
        for _ in range(max_it):
            # losowanie dwoch roznych, niesasiednich krawedzi: (i,i+1) oraz (j,j+1), j >= i+2;
            # krawedz (0, n-1) jest sasiednia z (n-1, 0) tj. i=0, j=n-1 - pomijamy.
            i = losint(n - 2)
            j = losint(i + 2, n)
            if i == 0 and j == n - 1:
                continue
            a, b = cykl[i], cykl[i + 1]
            c, d = cykl[j], cykl[(j + 1) % n]
            delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
            if delta < 0 or los() < math.exp(-delta / T):
                cykl[i + 1:j + 1] = cykl[i + 1:j + 1][::-1]
                dl += delta
                if dl < najlepsza_dl - 1e-12:
                    najlepszy, najlepsza_dl = list(cykl), dl
    # dl akumulowane przyrostami - przeliczamy dla uniknięcia dryfu bledu zmiennoprzecinkowego
    return najlepszy, dlugosc_cyklu(najlepszy, dist), cykl


def rysuj(punkty, cykl, tytul, plik=None):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = [punkty[v][0] for v in cykl] + [punkty[cykl[0]][0]]
    ys = [punkty[v][1] for v in cykl] + [punkty[cykl[0]][1]]
    ax.plot(xs, ys, "-o", markersize=3, linewidth=1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(tytul)
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    if plik:
        fig.savefig(plik, dpi=150)
    return fig, plt


def parsuj_argumenty():
    ap = argparse.ArgumentParser(description="TSP: symulowane wyzarzanie z ruchem 2-opt")
    ap.add_argument("--plik", default=PLIK_PUNKTOW)
    ap.add_argument("--chlodzenie", choices=["kwadratowe", "liniowe", "wykladnicze"], default=CHLODZENIE)
    ap.add_argument("--kroki-chlodzenia", type=int, default=KROKI_CHLODZENIA)
    ap.add_argument("--t-start", type=float, default=T_START)
    ap.add_argument("--t-koniec", type=float, default=T_KONIEC)
    ap.add_argument("--max-it", type=int, default=MAX_IT)
    ap.add_argument("--powtorzen", type=int, default=POWTORZEN)
    ap.add_argument("--ziarno", type=int, default=ZIARNO)
    ap.add_argument("--wykres", default=PLIK_WYKRESU, help="plik PNG z wynikiem")
    ap.add_argument("--bez-okna", action="store_true", default=not POKAZ_OKNO)
    ap.add_argument("--start-od-zera", action="store_true", default=not START_Z_NAJLEPSZEGO,
                    help="kazde powtorzenie startuje od cyklu z pliku zamiast od najlepszego")
    return ap.parse_args()


def main():
    arg = parsuj_argumenty()
    if arg.ziarno is not None:
        random.seed(arg.ziarno)
    if arg.t_start <= 0 or arg.t_koniec <= 0:
        raise SystemExit("temperatury musza byc dodatnie")
    if arg.max_it < 1 or arg.powtorzen < 1 or arg.kroki_chlodzenia < 1:
        raise SystemExit("max-it, powtorzen i kroki-chlodzenia musza byc >= 1")

    punkty = wczytaj_punkty(arg.plik)
    n = len(punkty)
    if n < 4:
        raise SystemExit(f"za malo punktow ({n}); potrzeba co najmniej 4")
    dist = macierz_odleglosci(punkty)
    temperatury = harmonogram_temperatur(arg.chlodzenie, arg.kroki_chlodzenia, arg.t_start, arg.t_koniec)

    cykl0 = list(range(n))                      # cykl poczatkowy: kolejnosc z pliku
    dl0 = dlugosc_cyklu(cykl0, dist)
    print(f"Punktow: {n}, cykl poczatkowy (kolejnosc z pliku): dlugosc = {dl0:.3f}")
    print(f"Chlodzenie: {arg.chlodzenie}, T: {temperatury[0]:.4g} -> {temperatury[-1]:.4g}, "
          f"{len(temperatury)} poziomow x {arg.max_it} iteracji")

    najlepszy, najlepsza_dl = cykl0, dl0
    for k in range(1, arg.powtorzen + 1):
        start = najlepszy if not arg.start_od_zera else cykl0
        cykl, dl, _ = symulowane_wyzarzanie(start, dist, temperatury, arg.max_it)
        print(f"  powtorzenie {k}/{arg.powtorzen}: dlugosc = {dl:.3f}")
        if dl < najlepsza_dl:
            najlepszy, najlepsza_dl = cykl, dl

    print(f"\nNajkrotszy znaleziony cykl: dlugosc = {najlepsza_dl:.3f}")
    assert sorted(najlepszy) == list(range(n)), "wynik nie jest cyklem Hamiltona"

    fig0, plt = rysuj(punkty, cykl0, f"Cykl poczatkowy, dlugosc: {dl0:.3f}")
    fig1, _ = rysuj(punkty, najlepszy, f"Cykl wyjsciowy, dlugosc: {najlepsza_dl:.3f}", arg.wykres)
    if arg.wykres:
        print(f"Wykres zapisano w {arg.wykres}")
    if not arg.bez_okna:
        plt.show()


if __name__ == "__main__":
    main()
