import folium

def plot_route_on_map(graph, route):
    """
    Plots the rider's route on a Folium map.
    
    Parameters:
    - graph: The street network graph.
    - route: List of nodes representing the route.
    
    Returns:
    - Folium map object with the route plotted.
    """
    start_node = route[0]
    map_center = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])
    my_map = folium.Map(location=map_center, zoom_start=14)

    # Extract lat/lon points from route nodes
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]

    # Plot the route on the map
    folium.PolyLine(route_coords, color='blue', weight=5).add_to(my_map)

    return my_map
