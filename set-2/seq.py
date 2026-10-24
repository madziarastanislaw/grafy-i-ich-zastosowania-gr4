import matplotlib.pyplot as plt
import networkx as nx
import sys
import random

def sort_elem(T: list):
    return T[0] #założenie, że indeks jest na 1, a stopień na 0

def randomize(edges: list, trialNum: int, G):
    for _ in range(0,trialNum):
        fst = random.randint(0, len(edges)-1)
        snd = random.randint(0, len(edges)-1)
        if fst != snd:
            elem1 = edges[fst]
            elem2 = edges[snd]
            edges.remove(elem1)
            edges.remove(elem2)
            if elem1[0] == elem2[1] or elem1[1] == elem2[0]:
                edges.append(elem1)
                edges.append(elem2)
            else:
                edges.append([elem1[0], elem2[1]])
                edges.append([elem1[1], elem2[0]])
    G.add_edges_from(edges)


def seq_check(L: list, G):
    G.add_nodes_from([i for i in range(0,len(L))])
    edges = []
    while True:
        L.sort(reverse=True,key=sort_elem)
        if L[0][0] == 0: #zakładając, że po sortowaniu 0 jest pierwsze i nie ma liczb ujemnych (w 1 runie), to ten warunek jest wystarczający
            if CODE == "randomize" or CODE == "spskl":
                randomize(edges, len(L), G)
            return True
        for i in range(1,L[0][0]+1):
            if CODE == "standard":
                G.add_edge(L[0][1],L[i][1])
            else:
                edges.append([L[0][1],L[i][1]])
            L[i] = [L[i][0] - 1, L[i][1]]
            if L[i][0] < 0:
                return False
        L[0] = [0, L[0][1]]


def components(G):
    #DFS na stosie zamiast rekurencji - brak limitu głębokości dla dużych grafów
    visited = set()
    all_sp = []
    for start in G.nodes:
        if start in visited:
            continue
        spSkl = []
        stack = [start]
        visited.add(start)
        while stack:
            node = stack.pop()
            spSkl.append(node)
            for i in G[node]: #sąsiedzi obecnego wierzchołka
                if i not in visited:
                    visited.add(i)
                    stack.append(i) #schodzenie wgłąb
        all_sp.append(sorted(spSkl))

    return all_sp

def largest_component(G):
    #zwraca podgraf będący największą spójną składową
    Skl = components(G)
    if not Skl:
        return G.copy()
    return G.subgraph(max(Skl, key=len)).copy()


if __name__ == "__main__":
    actualList = []
    try:
        inputList = []
        CODE = sys.argv[1].lower()
        if CODE != "standard" and CODE != "randomize" and CODE != "spskl":
            print("Code (first parameter) can only be 'standard' or 'randomize' or 'spskl' - nothing else!")
            sys.exit(1)
        for i in range(2, len(sys.argv)):
            inputList.append(int(sys.argv[i]))
        idx = 0
        for i in inputList:
            if int(i) < 0:
                print("Lists with integers less than 0 are not acceptable!")
                sys.exit(1)
            actualList.append([int(i), idx])
            idx += 1
    except ValueError:
        print("Input has to be a list of integers!")
        sys.exit(1)


    G = nx.Graph()
    if seq_check(actualList,G):
        if CODE == "spskl":
            Skl = components(G)
            print("Spójne składowe:")
            u = 1
            for i in Skl:
                print(f"{u}) " + " ".join(str(v) for v in i))
                u += 1
            print(f"Najwieksza skladowa ma numer {Skl.index(max(Skl, key=len)) + 1}.")
        nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
        plt.show()
    else:
        print("This is not a graphic sequence!")
