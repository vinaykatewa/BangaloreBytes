# import osmnx as ox
# import networkx as nx
# import matplotlib.pyplot as plt
# import pickle
# from osmnx._errors import GraphSimplificationError

# # Define the center of Bangalore and the area to extract
# center_point = (12.9716, 77.5946)  # Latitude and longitude of Bangalore city center
# distance = 5000  # 5 km radius

# # Download the street network
# G = ox.graph_from_point(center_point, dist=distance, network_type='drive')

# # Try to simplify the graph, but handle the case where it's already simplified
# try:
#     G = ox.simplify_graph(G)
# except GraphSimplificationError:
#     print("Graph is already simplified.")

# # Convert the graph to undirected (if your Q-learning model doesn't need direction information)
# G = G.to_undirected()

# # Plot the graph
# fig, ax = ox.plot_graph(G, show=False, close=False)

# # Save the plot as an image
# plt.savefig('bangalore_map.png')
# plt.close()

# # Save the graph object for later use
# with open('bangalore_graph.pkl', 'wb') as f:
#     pickle.dump(G, f)

# # Print some basic stats about the graph
# print(f"Number of nodes: {len(G.nodes)}")
# print(f"Number of edges: {len(G.edges)}")

# # Function to get node coordinates
# def get_node_coordinates(node_id):
#     return (G.nodes[node_id]['y'], G.nodes[node_id]['x'])

# # Example of how to access node and edge data
# print("\nExample node data:")
# print(list(G.nodes(data=True))[0])

# print("\nExample edge data:")
# print(list(G.edges(data=True))[0])

# print("\nTo use this graph in your Q-learning model, you can load it with:")
# print("with open('bangalore_graph.pkl', 'rb') as f:")
# print("    G = pickle.load(f)")
# print("Then use networkx functions to work with the graph.")

# # Additional information about the graph
# print("\nAdditional Graph Information:")
# print(f"Is the graph directed? {nx.is_directed(G)}")
# print(f"Is the graph connected? {nx.is_connected(G)}")
# if not nx.is_connected(G):
#     print(f"Number of connected components: {nx.number_connected_components(G)}")

# # Calculate and print some basic metrics
# print(f"\nAverage node degree: {sum(dict(G.degree()).values()) / len(G):.2f}")
# print(f"Graph diameter: {nx.diameter(G)}")
# print(f"Average shortest path length: {nx.average_shortest_path_length(G):.2f}")

import osmnx as ox
import pickle

def setup_bangalore_map(center_point=(12.9716, 77.5946), distance=5000, graph_file='bangalore_graph.pkl'):
    """
    Downloads the street network of Bangalore and saves it as a pickle file.
    
    Parameters:
    - center_point: Tuple (latitude, longitude) for the city center.
    - distance: Radius in meters for the graph extraction.
    - graph_file: File name to save the graph object.
    
    Returns:
    - None
    """
    # Download the street network
    G = ox.graph_from_point(center_point, dist=distance, network_type='drive')

    # Convert the graph to undirected for easier route finding
    G = G.to_undirected()

    # Save the graph object for later use
    with open(graph_file, 'wb') as f:
        pickle.dump(G, f)

    print(f"Graph successfully saved to {graph_file}")

if __name__ == "__main__":
    setup_bangalore_map()
