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

connected.py - 2 parametry jak w randoming.py; losuje wyłącznie spójny graf o zadanej liczbie wierzchołków (korzysta z randoming.py z set-1 oraz spójnych składowych z seq.py z set-2). Kończy się błędem, gdy liczba krawędzi jest mniejsza niż n-1 lub gdy w 100 próbach nie uda się wylosować grafu spójnego.

weighted.py - 2 lub 3 parametry: pierwszy - liczba wierzchołków, drugi - liczba krawędzi/prawdopodobieństwo (jak w randoming.py), trzeci (opcjonalny) - wierzchołek startowy dla algorytmu Dijkstry (domyślnie 1). Graf losowany jest przez connected.py, więc obowiązują te same ograniczenia (np. `weighted.py 12 20` lub `weighted.py 12 0.4 3`).

Wypisuje kolejno, każde zadanie pod nagłówkiem "=== Zadanie N ===":
- krawędzie spójnego grafu losowego z wagami 1-10 (zad. 1)
- najkrótsze ścieżki i ich długości z wierzchołka startowego - algorytm Dijkstry (zad. 2)
- macierz odległości - Dijkstra uruchomiony z każdego wierzchołka (zad. 3)
- tabelę z sumą odległości i odległością od najdalszego wierzchołka dla każdego wierzchołka, a pod nią centrum i centrum minimax (zad. 4); przy remisie wybierany jest wierzchołek o najmniejszym numerze
- minimalne drzewo rozpinające - algorytm Kruskala (zad. 5)

Na koniec rysuje graf z wagami oraz zaznaczone na niebiesko minimalne drzewo rozpinające.

Algorytmy Dijkstry i Kruskala są zaimplementowane samodzielnie na podstawie pseudokodu z alg_3.pdf.
