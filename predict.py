import pickle
import json
import pandas as pd
import osmnx as ox
import networkx as nx

# Load the saved Bangalore map
with open('bangalore_graph.pkl', 'rb') as f:
    G = pickle.load(f)

# Load trained Q-tables from Model 1 and Model 2
with open('q_table_model_1.json', 'r') as f:
    Q_table_model_1 = json.load(f)
    
with open('q_table_model_2.json', 'r') as f:
    Q_table_model_2 = json.load(f)

# Load new orders and riders data (for prediction)
new_order_data = pd.read_csv('new_order_data.csv')
new_rider_data = pd.read_csv('new_rider_data.csv')

# Function to get the nearest node in the graph
def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, X=lon, Y=lat)

# Function to calculate the route between two points
def calculate_route(source_node, target_node):
    try:
        return nx.shortest_path(G, source=source_node, target=target_node, weight='length')
    except nx.NetworkXNoPath:
        return None

# Initialize a list to store prediction results
prediction_results = []

# For each new order, predict the best rider and the optimal route
for order_index, order in new_order_data.iterrows():
    print(f"Predicting for Order {order_index + 1}/{len(new_order_data)} (Order ID: {order['Order ID']})")

    # Store individual order result
    order_result = {
        "Order ID": order['Order ID'],
        "Selected Rider": None,
        "Route Rider to Restaurant": None,
        "Route Restaurant to Delivery": None,
        "Additional Orders": []
    }

    # Get restaurant and delivery locations
    restaurant_lat = order['Restaurant Latitude']
    restaurant_lon = order['Restaurant Longitude']
    delivery_lat = order['Order Latitude']
    delivery_lon = order['Order Longitude']

    restaurant_node = get_nearest_node(restaurant_lat, restaurant_lon)
    delivery_node = get_nearest_node(delivery_lat, delivery_lon)

    # Use Model 1's Q-table to select the best rider
    state = f"order_{order['Order ID']}"
    if state in Q_table_model_1:
        rider_index = max(Q_table_model_1[state], key=Q_table_model_1[state].get)
        selected_rider = new_rider_data.iloc[int(rider_index)]  # Ensure rider_index is converted to int
        rider_node = get_nearest_node(selected_rider['Rider Latitude'], selected_rider['Rider Longitude'])

        # Store selected rider in result
        order_result["Selected Rider"] = selected_rider['Rider ID']

        print(f"Selected Rider {selected_rider['Rider ID']} for Order {order['Order ID']}. Finding route...")

        # Calculate the route from rider to restaurant
        route_rider_to_restaurant = calculate_route(rider_node, restaurant_node)
        if route_rider_to_restaurant is None:
            print(f"No path found between Rider {selected_rider['Rider ID']} and Restaurant.")
            continue

        # Store the route in result
        order_result["Route Rider to Restaurant"] = route_rider_to_restaurant

        # Calculate the route from restaurant to delivery destination
        route_restaurant_to_delivery = calculate_route(restaurant_node, delivery_node)
        if route_restaurant_to_delivery is None:
            print(f"No path found between Restaurant and Delivery location.")
            continue

        # Store the route in result
        order_result["Route Restaurant to Delivery"] = route_restaurant_to_delivery

        total_route = route_rider_to_restaurant + route_restaurant_to_delivery
        print(f"Total route found for Order {order['Order ID']}. Route length: {len(total_route)} nodes.")

        # Use Model 2 to determine additional orders and optimize route
        for idx, other_order in new_order_data.iterrows():
            if idx != order_index:
                other_delivery_node = get_nearest_node(other_order['Order Latitude'], other_order['Order Longitude'])
                if nx.shortest_path_length(G, source=restaurant_node, target=other_delivery_node, weight='length') <= 1000:
                    state = f"order_{order['Order ID']}_additional_{other_order['Order ID']}"
                    if state in Q_table_model_2:
                        action = max(Q_table_model_2[state], key=Q_table_model_2[state].get)
                        
                        if action == 1:  # Pick up additional order
                            print(f"Picked up additional Order {other_order['Order ID']}.")
                            order_result["Additional Orders"].append(other_order['Order ID'])
                        else:
                            print(f"Skipped additional Order {other_order['Order ID']}.")

    else:
        print(f"No trained state for Order {order['Order ID']}.")

    # Append this order's result to the overall results list
    prediction_results.append(order_result)

    print("-" * 50)

print("Prediction complete.")

# Return or save the results
for result in prediction_results:
    print(result)

