import matplotlib.pyplot as plt
import networkx as nx
import sys

def random_graph(N, MP):
    #MP jako float -> G(n,p), jako int -> G(n,l)
    if N < 1:
        raise ValueError("Number of nodes must be at least 1!")

    if isinstance(MP,float):
        if MP < 0 or MP > 1:
            raise ValueError("Probability must be in range [0, 1]!")
        return nx.erdos_renyi_graph(n=N, p=MP)

    if MP < 0 or MP > N*(N-1)//2:
        raise ValueError(f"Number of edges must be in range [0, {N*(N-1)//2}]!")
    return nx.gnm_random_graph(n=N, m=MP)


if __name__ == "__main__":
    #sprawdzanko
    if len(sys.argv) < 3:
        print("Usage: randoming.py <nodes> <edges (int) | probability (float)>")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        if '.' in sys.argv[2]:
            MP = float(sys.argv[2])
        else:
            MP = int(sys.argv[2])
    except ValueError:
        print("Input values must be an integer and integer/float")
        sys.exit(1)

    try:
        G = random_graph(N, MP)
    except ValueError as e:
        print(e)
        sys.exit(1)

    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()
