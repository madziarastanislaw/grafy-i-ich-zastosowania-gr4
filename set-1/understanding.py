import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import sys

def inform(row, col, input, reason):
    print(f"Value in row: {row} & column: {col} is invalid for given input type: {input}.")
    print(reason)


def check_nibor(A):
    if(not np.array_equal(A,A.T)):
        print("This array is not a proper neighbourhood matrix - its not symmetrical!")
        return False

    for i in range(0,len(A)):
        if(A[i][i] != 0):
            inform(i,i,"nibor", "Value on the diagonal must be 0!")
            return False
            
    return True

def check_list(A):
    l = len(A)
    row = 1
    for i in A:
        if max(i) > l:
            inform(row,i.index(max(i)), "list", "Value cannot be greater than the row number!")
            return False

        if  len(i) >= l:
            inform(row,l, "list", "Value cannot exceed the ammount of nodes!")
            return False

        if len(i) != len(set(i)):
            inform(row,"---", "list", "Values cannot repeat!")
            return False
        row+=1

    return True

def check_incydent(A):
    colN = 1
    for col in A.T:
        if(sum(col) != 2):
            inform("---",colN,"incydent", "Sum of values in columns must be equal to 2!")
            return False
        colN+=1

    return True


data_matrix = []
row_counter = 0
col_counter = 0

input_type = ""

try:
    with open("demo.txt","rt") as fin:
        for line in fin:
            row_counter += 1
            num_tab = line.split()

            row = []
            for i in num_tab:
                col_counter += 1

                if(row_counter == 1):
                    if('.' in num_tab[0]):
                        input_type = "list"
                    elif(int(num_tab[0])==0):
                        input_type = "nibor"
                    else:
                        input_type = "incydent"

                if(col_counter == 1 and input_type == "list"):
                    continue

                row.append(int(i))
                
                if(row[-1] < 0 or (row[-1]>1 and input_type != "list")):
                    raise ValueError
        
            col_counter = 0

            data_matrix.append(row)

except ValueError:
    if input_type == "list":
        inform(row_counter,col_counter,input_type, "Values must be integers greter than 0!")
    else:
        inform(row_counter,col_counter,input_type, "Values must be inteers either 0 or 1!")
    sys.exit(1)

if input_type!="list":
    try:
        N = np.array(data_matrix)
    except ValueError:
        print("The data provided is not any form of a matrix!")

    if input_type == "nibor" and check_nibor(N):
        A = np.array(data_matrix)
        G = nx.from_numpy_array(A)
        nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
        plt.show()

    elif input_type == "incydent" and check_incydent(N):
        G = nx.Graph()
        n = len([i[0] for i in data_matrix])
        G.add_nodes_from([i for i in range(1, n+1)])

        edge_list = []
        N = np.array(data_matrix)
        for i in N.T:
            idx = [j+1 for j,x in enumerate(i) if x == 1]
            if (idx[0],idx[1]) not in edge_list:
                edge_list.append((idx[1],idx[0]))

        G.add_edges_from(edge_list)
        nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
        plt.show()

elif check_list(data_matrix):
    G = nx.Graph()
    G.add_nodes_from([i for i in range(1,len(data_matrix)+1)])

    edge_list = []
    for i in range(1, len(data_matrix)+1):
        for j in data_matrix[i-1]:
            if (j,i) not in edge_list:
                edge_list.append((i,j))

    G.add_edges_from(edge_list)
    nx.draw(G, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray", font_size=12, pos=nx.circular_layout(G))
    plt.show()


