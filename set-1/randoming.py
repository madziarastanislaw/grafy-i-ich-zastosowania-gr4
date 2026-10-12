import matplotlib.pyplot as plt
import networkx as nx
import sys

#sprawdzanko
try:
    N = int(sys.argv[1])
    if '.' in sys.argv[2]:
        MP = float(sys.argv[2])
    else:
        MP = int(sys.argv[2])
except ValueError:
    print("Input values must be an integer and integer/float")
    sys.exit(1)


if isinstance(MP,float) and MP > 0 and MP < 1:
    G =nx.erdos_renyi_graph(n=N, p=MP)

elif isinstance(MP,int) and MP > 0 and MP < N*(N-1)/2:
    G = nx.gnm_random_graph(n=N, m=MP)


nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
plt.show()