import argparse
import math
import random

#Zadanie 2 - problem komiwojażera: symulowane wyżarzanie (Metropolis-Hastings) z ruchami 2-opt (Algorytm 1 z alg_6.pdf)
#Wejście: plik ze współrzędnymi punktów, w każdej linii "x y"; cykl początkowy = kolejność punktów z pliku

#wartości domyślne - każdą można nadpisać flagą z linii poleceń (python zad2_tsp.py --help)
PLIK_PUNKTOW = "xqf131.dat.txt"

CHLODZENIE = "kwadratowe"   #"kwadratowe" | "liniowe" | "wykladnicze"
KROKI_CHLODZENIA = 100      #liczba poziomów temperatury (w pseudokodzie: i = 100 ... 2)
T_START = 10.0              #temperatura początkowa (0.001 * 100^2 = 10)
T_KONIEC = 0.004            #temperatura końcowa (0.001 * 2^2 = 0.004)
MAX_IT = 50_000             #iteracji na jeden poziom temperatury (MAX_IT z pseudokodu)
POWTORZEN = 5               #ile razy powtórzyć całą procedurę
START_Z_NAJLEPSZEGO = True  #kolejne powtórzenia startują od najlepszego dotąd cyklu
ZIARNO = None               #None = losowo, liczba całkowita = powtarzalne wyniki
PLIK_WYKRESU = "cykl_wynik.png" #None/"" = nie zapisuj
POKAZ_OKNO = True           #czy otworzyć okno z wykresami


def wczytaj_punkty(sciezka):
    #każda niepusta linia to "x y" (rozdzielone białymi znakami); linie zaczynające się od # są pomijane
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
    #odległości euklidesowe między wszystkimi parami punktów (liczone raz, żeby nie liczyć pierwiastków w pętli wyżarzania)
    n = len(punkty)
    return [[math.hypot(punkty[i][0] - punkty[j][0], punkty[i][1] - punkty[j][1])
             for j in range(n)] for i in range(n)]


def dlugosc_cyklu(cykl, dist):
    #suma długości krawędzi cyklu, łącznie z powrotem do pierwszego wierzchołka
    return sum(dist[cykl[i]][cykl[(i + 1) % len(cykl)]] for i in range(len(cykl)))


def harmonogram_temperatur(rodzaj, kroki, t_start, t_koniec):
    #lista temperatur malejąco od t_start do t_koniec, 'kroki' poziomów (chłodzenie dowolne wg alg_6.pdf)
    if kroki < 2:
        return [t_start]
    if rodzaj == "liniowe":
        return [t_start + (t_koniec - t_start) * k / (kroki - 1) for k in range(kroki)]
    if rodzaj == "wykladnicze":
        q = (t_koniec / t_start) ** (1.0 / (kroki - 1)) #stały iloraz kolejnych temperatur
        return [t_start * q ** k for k in range(kroki)]
    if rodzaj == "kwadratowe":
        #T proporcjonalne do i^2, gdzie i maleje liniowo (jak T = 0.001 i^2 w pseudokodzie); końce dokładnie t_start i t_koniec
        a, b = math.sqrt(t_start), math.sqrt(t_koniec)
        return [(a + (b - a) * k / (kroki - 1)) ** 2 for k in range(kroki)]
    raise ValueError(f"nieznany rodzaj chlodzenia: {rodzaj}")


def symulowane_wyzarzanie(cykl_start, dist, temperatury, max_it):
    #Algorytm 1 z alg_6.pdf. Ruch 2-opt: krawędzie (a,b), (c,d) -> (a,c), (b,d) przez odwrócenie fragmentu cyklu między b a c.
    #Różnica długości liczona w O(1) (d(Pnew) - d(P) = nowe krawędzie - stare krawędzie), a fragment odwracany tylko przy akceptacji ruchu.
    #Zwraca (najlepszy cykl, jego długość, ostatni cykl)
    cykl = list(cykl_start)
    n = len(cykl)
    dl = dlugosc_cyklu(cykl, dist)
    najlepszy, najlepsza_dl = list(cykl), dl
    if n < 4:
        return najlepszy, najlepsza_dl, cykl #2-opt nie ma sensu dla n < 4

    los = random.random
    losint = random.randrange
    for T in temperatury: #pętla chłodzenia (wyżarzanie: T maleje, czyli co poziom T zaczyna się nowy łańcuch Markowa)
        #ŁAŃCUCH MARKOWA: stanem jest aktualny cykl, a każdy krok max_it poniżej tworzy następny stan
        #wyłącznie z obecnego cyklu i losowania (bez pamięci o wcześniejszych cyklach); dla ustalonej T przejścia są stałe
        for _ in range(max_it): #pętla po iteracjach dla ustalonej T = kolejne kroki łańcucha Markowa
            #METROPOLIS-HASTINGS, część 1 - PROPOZYCJA nowego stanu: ruch 2-opt na dwóch losowych krawędziach;
            #propozycja jest symetryczna (to samo odwrócenie fragmentu cofa ruch), więc w warunku akceptacji zostaje sam wzór Metropolisa
            #losowanie dwóch różnych, niesąsiednich krawędzi (i,i+1) oraz (j,j+1), j >= i+2;
            #krawędź (0,1) i (n-1,0) mają wspólny wierzchołek 0, więc parę i=0, j=n-1 pomijamy
            i = losint(n - 2)
            j = losint(i + 2, n)
            if i == 0 and j == n - 1:
                continue
            a, b = cykl[i], cykl[i + 1]
            c, d = cykl[j], cykl[(j + 1) % n]
            delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
            #METROPOLIS-HASTINGS, część 2 - AKCEPTACJA (reguła Metropolisa):
            #krótszy cykl zawsze akceptujemy, dłuższy z prawdopodobieństwem exp(-delta/T)
            #jeśli ruch nie zostanie zaakceptowany, łańcuch zostaje w tym samym stanie (cykl bez zmian)
            if delta < 0 or los() < math.exp(-delta / T):
                cykl[i + 1:j + 1] = cykl[i + 1:j + 1][::-1] #przejście do nowego stanu: odwrócenie fragmentu między b a c
                dl += delta
                if dl < najlepsza_dl - 1e-12:
                    najlepszy, najlepsza_dl = list(cykl), dl
    #dl akumulowane przyrostami - długość najlepszego cyklu przeliczamy od nowa, żeby uniknąć dryfu błędu zmiennoprzecinkowego
    return najlepszy, dlugosc_cyklu(najlepszy, dist), cykl


def rysuj(punkty, cykl, tytul, plik=None):
    #rysuje cykl (z domknięciem do pierwszego punktu); gdy podano plik - zapisuje go jako PNG
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

    cykl0 = list(range(n)) #cykl początkowy: kolejność z pliku
    dl0 = dlugosc_cyklu(cykl0, dist)
    print(f"Punktow: {n}, cykl poczatkowy (kolejnosc z pliku): dlugosc = {dl0:.3f}")
    print(f"Chlodzenie: {arg.chlodzenie}, T: {temperatury[0]:.4g} -> {temperatury[-1]:.4g}, "
          f"{len(temperatury)} poziomow x {arg.max_it} iteracji")

    #procedurę powtarzamy wielokrotnie, bo wynik jest losowy; zapamiętujemy najlepszy cykl
    najlepszy, najlepsza_dl = cykl0, dl0
    for k in range(1, arg.powtorzen + 1):
        start = najlepszy if not arg.start_od_zera else cykl0
        cykl, dl, _ = symulowane_wyzarzanie(start, dist, temperatury, arg.max_it)
        print(f"  powtorzenie {k}/{arg.powtorzen}: dlugosc = {dl:.3f}")
        if dl < najlepsza_dl:
            najlepszy, najlepsza_dl = cykl, dl

    print(f"\nNajkrotszy znaleziony cykl: dlugosc = {najlepsza_dl:.3f}")
    assert sorted(najlepszy) == list(range(n)), "wynik nie jest cyklem Hamiltona" #każdy punkt dokładnie raz

    #rys. 2(a) i 2(b) z input_6.pdf: cykl początkowy i wynikowy
    fig0, plt = rysuj(punkty, cykl0, f"Cykl poczatkowy, dlugosc: {dl0:.3f}")
    fig1, _ = rysuj(punkty, najlepszy, f"Cykl wyjsciowy, dlugosc: {najlepsza_dl:.3f}", arg.wykres)
    if arg.wykres:
        print(f"Wykres zapisano w {arg.wykres}")
    if not arg.bez_okna:
        plt.show()


if __name__ == "__main__":
    main()
