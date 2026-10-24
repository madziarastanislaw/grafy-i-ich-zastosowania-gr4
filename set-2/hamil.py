import matplotlib.pyplot as plt
import networkx as nx
import sys
import random


def seq_check(L: list, G):

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

    G.add_nodes_from([i for i in range(0,len(L))])
    edges = []
    while True:
        L.sort(reverse=True,key=sort_elem)
        if L[0][0] == 0: #zakładając, że po sortowaniu 0 jest pierwsze i nie ma liczb ujemnych (w 1 runie), to ten warunek jest wystarczający
            randomize(edges, len(L), G)
            return True
        for i in range(1,L[0][0]+1):
            #G.add_edge(L[0][1],L[i][1])
            edges.append([L[0][1],L[i][1]])
            L[i] = [L[i][0] - 1, L[i][1]]
            if L[i][0] < 0:
                return False
        L[0] = [0, L[0][1]]


def Hammiltoning(G):
    def hamil_req(heap,node, G):
        nibors = list(G[node])
        for i in nibors:
            if i not in heap:
                heap.append(i)
                hamil_req(heap,i,G)
                
                if len(heap) > N:
                    return
        if len(heap) < N:
            heap.pop(-1)
        else:
            if heap[0] != heap[-1]:
                if heap[0] not in nibors:
                    heap.pop(-1)
                else:
                    heap.append(heap[0])
            
    heap = []
    nodes = list(G.nodes)
    N = len(nodes)
    for i in nodes:
        heap.append(i)
        hamil_req(heap,i,G)
        if len(heap) == len(nodes)+1:
            return heap
        heap = []
    return False


actualList = []
try:
    inputList = []
    for i in range(1, len(sys.argv)):
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
    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()
    win = Hammiltoning(G)
    if not win:
        print("No Hammiltonian cycle could be found for this graph!")
        print(win)
    else:
        print("Found the Hammiltonian cycle:")
        stri = f"{win[0]} "
        for i in range(1,len(win)):
            stri += f"-> {win[i]} "
        print(stri)