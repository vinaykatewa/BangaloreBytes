import pickle

def load_bangalore_map(graph_file='bangalore_graph.pkl'):
    """
    Loads the Bangalore graph from the pickle file.
    
    Parameters:
    - graph_file: The file name where the graph object is saved.
    
    Returns:
    - graph: The loaded graph object.
    """
    with open(graph_file, 'rb') as f:
        G = pickle.load(f)

    print(f"Graph loaded successfully with {len(G.nodes)} nodes and {len(G.edges)} edges.")
    return G

if __name__ == "__main__":
    G = load_bangalore_map() 