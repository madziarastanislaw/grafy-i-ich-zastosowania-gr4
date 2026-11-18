# grafy-i-ich-zastosowania-gr4

Wymagania: Python z bibliotekami `networkx`, `matplotlib` i `numpy` - instalacja: `pip install -r requirements.txt`

set-1:
2 pliki: randoming.py oraz understanding.py

randoming.py - 2 parametry: pierwszy - liczba wierzchołków, drugi - liczba krawędzi (liczba całkowita, model G(n,l)) / prawdopodobieństwo (liczba z kropką, np. 0.5, model G(n,p))
understanding - 1 lub 2 parametry:
- dla 1 parametru: ścieżka do pliku tekstowego generującego graf
- dla 2 parametrów: Pierwszy: wartość tekstowa ("Neighbourhood"/"List"/"Incidence") - to na co chcesz konwertować, Drugi: ścieżka do pliku

set-2:
3 pliki: seq.py, euler.py oraz kreg.py

seq.py - pierwszy parametr: tryb, kolejne: ciąg liczb naturalnych (np. `seq.py standard 4 2 2 3 2 1 4 2 2 2 2`)
- "standard": sprawdza czy ciąg jest graficzny i rysuje zbudowany graf (zad. 1)
- "randomize": jak wyżej, dodatkowo randomizuje krawędzie zamianą ab, cd -> ad, bc (zad. 2)
- "spskl": jak "randomize", dodatkowo wypisuje spójne składowe i numer największej z nich (zad. 3)

euler.py - 1 parametr: liczba wierzchołków (>= 5); losuje graf eulerowski i wypisuje cykl Eulera (zad. 4)
kreg.py - 2 parametry: liczba wierzchołków, stopień k; tworzy graf k-regularny (zad. 5)

Zadanie 6 (graf hamiltonowski) - brak.

set-3:
2 pliki: connected.py oraz weighted.py (wszystkie zadania na jednym wylosowanym grafie)

connected.py - 2 parametry: liczba wierzchołków (int) oraz liczba krawędzi (int) -> G(n,l) lub prawdopodobieństwo (ułamek dziesiętny, np. 0.3) -> G(n,p); inne zapisy (1e-1, inf, 5.0 jako liczba wierzchołków itp.) są odrzucane. Losuje wyłącznie spójny graf o wierzchołkach 1..n: graf G(n,l)/G(n,p) generowany jest ręcznie zaimplementowanym modelem Erdősa-Rényiego (funkcja random_graph), a spójność sprawdzana spójnymi składowymi z seq.py z set-2; niespójne grafy są odrzucane i losowane ponownie. Kończy się błędem, gdy liczba krawędzi jest mniejsza niż n-1 lub gdy w 100 próbach nie uda się wylosować grafu spójnego.

weighted.py - 2 lub 3 parametry: pierwszy - liczba wierzchołków, drugi - liczba krawędzi/prawdopodobieństwo (jak w connected.py), trzeci (opcjonalny) - wierzchołek startowy dla algorytmu Dijkstry (domyślnie 1). Graf losowany jest przez connected.py, więc obowiązują te same ograniczenia (np. `weighted.py 12 20` lub `weighted.py 12 0.4 3`).

Wypisuje kolejno, każde zadanie pod nagłówkiem "=== Zadanie N ===":
- krawędzie spójnego grafu losowego z wagami 1-10 (zad. 1)
- najkrótsze ścieżki i ich długości z wierzchołka startowego - algorytm Dijkstry (zad. 2)
- macierz odległości - Dijkstra uruchomiony z każdego wierzchołka; z etykietami wierszy (od) i kolumn (do) (zad. 3)
- tabelę z sumą odległości i odległością od najdalszego wierzchołka dla każdego wierzchołka, a pod nią centrum i centrum minimax (zad. 4); przy remisie wybierany jest wierzchołek o najmniejszym numerze
- minimalne drzewo rozpinające - algorytm Kruskala (zad. 5)

Na koniec rysuje graf z wagami oraz zaznaczone na niebiesko minimalne drzewo rozpinające.

Algorytmy Dijkstry i Kruskala są zaimplementowane samodzielnie na podstawie pseudokodu z alg_3.pdf.

set-4:
3 pliki: digraph.py, kosaraju.py oraz johnson.py (johnson.py wykonuje wszystkie zadania na jednym digrafie) + pliki demo z przykładowym digrafem z input_4.pdf.
Uruchamiać z katalogu set-4 (`cd set-4`), bo ścieżki do plików demo są względne.

Szybki start:
- `python johnson.py rand 7 0.3` - zad. 1-4 na losowym digrafie (Bellman-Ford z wierzchołka 1)
- `python johnson.py rand 7 0.3 4` - to samo, Bellman-Ford z wierzchołka 4
- `python johnson.py inc-m demo_inc_m_w.txt` - przykład z input_4.pdf, odtwarza macierz odległości z listingu 4

Gdzie są zadania:
- zad. 1 - digraph.py (osobno: `python digraph.py ...`)
- zad. 2 - kosaraju.py (osobno: `python kosaraju.py ...`)
- zad. 3 - johnson.py: random_strongly_connected (kosaraju.py), random_weights, bellman_ford
- zad. 4 - johnson.py: add_s, johnson

Zadania 3 i 4 nie mają osobnych programów - korzystają z wyników poprzednich zadań (zad. 3 potrzebuje silnie spójnego digrafu z zad. 1-2, zad. 4 - digrafu z wagami z zad. 3), więc uruchamia się je przez johnson.py, który wykonuje zad. 1-4 po kolei.

Parametry wspólne dla wszystkich trzech programów - digraf podawany na jeden z dwóch sposobów:
- `rand <n> <p>` - losowy digraf G(n,p); n - liczba całkowita, p - ułamek dziesiętny (np. 0.3); inne zapisy (1e-1, 5.0 jako n itp.) są odrzucane
- `<adj-l | adj-m | inc-m> <plik>` - digraf wczytany z pliku w podanej reprezentacji:
  - adj-l - lista sąsiedztwa: wiersz `i. v1 v2 ...` (następniki wierzchołka i; wiersz `i.` bez wierzchołków, gdy brak łuków wychodzących)
  - adj-m - macierz sąsiedztwa n x n z 0/1 (1 w wierszu i, kolumnie j = łuk i -> j)
  - inc-m - macierz incydencji n x m (kolumna = łuk: -1 w wierszu początku, 1 w wierszu końca); opcjonalnie ostatni wiersz `w: w1 ... wm` z wagami łuków z kolejnych kolumn (wagi mogą być ujemne lub 0, dlatego nie są wpisywane w samą macierz, w której -1/1 oznacza kierunek)

  Niepoprawny plik (zła etykieta wiersza, pętla, powtórzony łuk, wartość spoza zakresu, niekwadratowa macierz, kolumna incydencji bez dokładnie jednego -1 i jednego 1, zła liczba wag itp.) kończy program komunikatem błędu ze wskazaniem linii/kolumny.

Pliki demo (ten sam digraf z input_4.pdf): demo_adj_l.txt, demo_adj_m.txt, demo_inc_m.txt - bez wag (rys. 1, listingi 1-3); demo_inc_m_w.txt - z wagami z rys. 2.

digraph.py - kodowanie digrafów i losowanie G(n,p) (zad. 1), np. `python digraph.py adj-l demo_adj_l.txt` lub `python digraph.py rand 7 0.3`. Wypisuje digraf we wszystkich trzech reprezentacjach (w tym samym formacie co pliki wejściowe, więc wynik można zapisać i wczytać ponownie; dla digrafu z wagami macierz incydencji z wierszem `w:`) i go rysuje (z wagami, jeśli są). G(n,p) zaimplementowane ręcznie: każda uporządkowana para (i, j), i != j, niezależnie z prawdopodobieństwem p daje łuk i -> j.

kosaraju.py - silnie spójne składowe algorytmem Kosaraju (zad. 2), np. `python kosaraju.py rand 8 0.2` lub `python kosaraju.py adj-l demo_adj_l.txt`. Wypisuje wierzchołki kolejnych składowych i informację, czy digraf jest silnie spójny; rysuje digraf z wierzchołkami pokolorowanymi wg składowej.

Uruchamianie zad. 3 i 4 (wynik pod nagłówkami "=== Zadanie 3 ===" i "=== Zadanie 4 ==="):
- `python johnson.py rand 7 0.3` - losowy digraf, Bellman-Ford z wierzchołka 1
- `python johnson.py rand 7 0.3 4` - Bellman-Ford z wierzchołka 4
- `python johnson.py inc-m demo_inc_m_w.txt` - digraf z wagami z input_4.pdf; macierz z zad. 4 = listing 4
- `python johnson.py adj-l demo_adj_l.txt` - ten sam digraf z pliku, wagi losowane

Zad. 3 (johnson.py) - losowy silnie spójny digraf z wagami i algorytm Bellmana-Forda:
- digraf silnie spójny: dla `rand` - jeśli digraf z zad. 1 nie jest silnie spójny, losowany jest nowy G(n,p) aż Kosaraju zwróci jedną składową (do 100 prób); dla pliku - digraf musi być silnie spójny, inaczej program kończy się po zad. 2
- wagi: losowane z [-5, 10]; gdy powstanie cykl o ujemnej wadze (wykrywany Bellmanem-Fordem), wszystkie wagi są losowane ponownie (do 100 prób). Dla pliku inc-m z wierszem `w:` używane są wagi z pliku (cykl o ujemnej wadze = błąd)
- wypisuje macierz incydencji z wagami oraz najkrótsze ścieżki i ich długości z wierzchołka startowego (Bellman-Ford, alg. 4 z alg_4.pdf), np.:
  `d(7) = -5 ==> [1 - 5 - 7]`

Zad. 4 (johnson.py) - algorytm Johnsona (alg. 5-6 z alg_4.pdf): dodaje wierzchołek s = 0 z łukami s -> v o wadze 0, Bellmanem-Fordem z s wyznacza h[v], przeskalowuje wagi na nieujemne w'(u,v) = w(u,v) + h[u] - h[v], uruchamia Dijkstrę (z set-3) z każdego wierzchołka i odtwarza odległości D[u][v] = d'(u,v) - h[u] + h[v]. Wypisuje macierz odległości z etykietami wierszy (od) i kolumn (do).

johnson.py - uruchamia zad. 1-4 na jednym digrafie: `python johnson.py rand <n> <p> [start]` lub `python johnson.py <adj-l | adj-m | inc-m> <plik> [start]`, start - wierzchołek startowy Bellmana-Forda (domyślnie 1). Każde zadanie wypisywane pod nagłówkiem "=== Zadanie N ===". Na koniec rysuje digraf z zad. 1-2 (kolory = składowe) obok digrafu z wagami z zad. 3-4.

Zalecane parametry: n do ok. 10 przy p ok. 0.2-0.3. Dla gęstszych digrafów wagi z [-5, 10] prawie zawsze tworzą cykl o ujemnej wadze i program kończy się błędem po 100 próbach.

Kosaraju, Bellman-Ford i Johnson są zaimplementowane samodzielnie na podstawie pseudokodu z alg_4.pdf.

set-6:
2 pliki: zad1_pagerank.py (zad. 1) oraz zad2_tsp.py (zad. 2) + pliki danych: demo_adj_l.txt, demo_adj_m.txt, demo_inc_m.txt (digraf z input_6.pdf, listing 1, w trzech reprezentacjach z set-4; wierzchołki A-L = 1-12) i xqf131.dat.txt (131 punktów do zad. 2).
Uruchamiać z katalogu set-6 (`cd set-6`), bo ścieżki do plików podawanych na wejściu są względne. Zad. 1 korzysta z set-4/digraph.py, więc wymaga `networkx` (jak set-4).
Na górze każdego programu są stałe z wartościami domyślnymi (wejście, parametry algorytmu); każdą z nich można też nadpisać flagą z linii poleceń (`--help` w zad. 1, w zad. 2 `python zad2_tsp.py --help`).

zad1_pagerank.py - PageRank dla digrafu, dwie metody na tym samym digrafie (d = 0.15 domyślnie):
- (a) błądzenie przypadkowe z teleportacją; PageRank = częstość odwiedzin po N krokach (domyślnie 1000000)
- (b) iteracja wektora obsadzeń p(t+1) = p(t)P, P_ij = (1-d)A_ij/d_i + d/n, od p(0) = (1/n, ..., 1/n) aż do zbieżności; gdy brak zbieżności w `--max-iter` krokach, wynikiem jest średnia wektorów
Wypisuje oba rankingi (od najważniejszego wierzchołka) oraz porównanie metod (maksymalna i średnia różnica wartości, zgodność kolejności).
Digraf podawany tak samo jak w set-4 (wierzchołki 1..n):
- `python zad1_pagerank.py` - przykład z input_6.pdf (demo_adj_l.txt); metoda (b) odtwarza listing 2(b), np. wierzchołek 9 (I) = 0.150941, 11 (K) = 0.029892
- `python zad1_pagerank.py adj-m demo_adj_m.txt` (też `adj-l`, `inc-m`) - digraf z pliku; formaty jak w set-4 (adj-l: `i. v1 v2 ...`, adj-m: macierz 0/1, inc-m: macierz incydencji -1/0/1); wymagane co najmniej jeden łuk wychodzący z każdego wierzchołka, inaczej błąd
- `python zad1_pagerank.py rand 12 0.3` - losowy digraf G(n,p) z set-4; wierzchołkom bez łuków wychodzących dolosowywany jest jeden łuk do innego wierzchołka
Opcje: `--d`, `--krokow`, `--eps`, `--max-iter`, `--ziarno` (powtarzalne wyniki), `--rysuj` (rysuje digraf).

zad2_tsp.py - problem komiwojażera, symulowane wyżarzanie (Metropolis-Hastings) z ruchami 2-opt (alg. 1 z alg_6.pdf): losowane są dwie różne, niesąsiednie krawędzie (a,b), (c,d), zamieniane na (a,c), (b,d) przez odwrócenie fragmentu cyklu między b a c. Różnica długości cyklu liczona jest w O(1), a fragment odwracany tylko przy akceptacji ruchu. Cykl początkowy = kolejność punktów z pliku. Wejście to plik ze współrzędnymi punktów (`x y` w linii), nie digraf.
- `python zad2_tsp.py` - xqf131.dat.txt, chłodzenie kwadratowe T: 10 -> 0.004 w 100 poziomach, 50000 iteracji na poziom, 5 powtórzeń (kolejne startują od najlepszego dotąd cyklu); rysuje cykl początkowy i wynikowy oraz zapisuje wynik do cykl_wynik.png
- `python zad2_tsp.py --chlodzenie liniowe` (też: wykladnicze, kwadratowe), `--max-it`, `--powtorzen`, `--t-start`, `--t-koniec`, `--kroki-chlodzenia`, `--ziarno`, `--plik`, `--start-od-zera`, `--bez-okna`, `--wykres <plik.png>`
Typowy wynik dla xqf131: długość ok. 567-570 (cykl początkowy: 4705.907).

PageRank i symulowane wyżarzanie są zaimplementowane samodzielnie na podstawie input_6.pdf i alg_6.pdf (matplotlib tylko do rysowania).
