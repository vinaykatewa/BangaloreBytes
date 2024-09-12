import pickle
import networkx as nx
import osmnx as ox
import pandas as pd
import numpy as np
import random
from collections import defaultdict
import json
import re
import time

# Load the saved Bangalore map
with open('bangalore_graph.pkl', 'rb') as f:
    G = pickle.load(f)

# Load rider data, order data, and Q-table from Model 1
rider_data = pd.read_csv('rider_data.csv')
order_data = pd.read_csv('order_data.csv')
with open('q_table_model_1.json', 'r') as f:
    Q_table_model_1 = json.load(f)

# Parameters for Q-learning in Model 2
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate

# Initialize Q-table for Model 2
Q_table_model_2 = defaultdict(lambda: {0: 0, 1: 0})

# Define the radius to search for nearby orders (e.g., 1 km)
SEARCH_RADIUS = 1000

# Function to get the nearest node in the graph
def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, X=lon, Y=lat)

# Function to calculate the route between two points
def calculate_route(source_node, target_node):
    try:
        return nx.shortest_path(G, source=source_node, target=target_node, weight='length')
    except nx.NetworkXNoPath:
        return None

# Function to select an action using ε-greedy policy (pick up or skip order)
def select_action(state, Q_table, epsilon):
    if random.uniform(0, 1) < epsilon:  # Exploration
        return random.choice([0, 1])  # 0: Skip, 1: Pick up
    else:  # Exploitation
        return max(Q_table[state], key=Q_table[state].get)
    
def increment_order_id(order_id):
    match = re.match(r'(\D+)(\d+)', order_id)  # Extract prefix and numeric part
    if match:
        prefix, number = match.groups()
        new_number = str(int(number) + 1).zfill(len(number))  # Increment and maintain leading zeros
        return f"{prefix}{new_number}"
    else:
        return order_id

# Function to update Q-values
def update_q_value(Q_table, state, action, reward, next_state, alpha, gamma):
    best_next_action = max(Q_table[next_state].values()) if Q_table[next_state] else 0
    current_q_value = Q_table[state][action]
    Q_table[state][action] = current_q_value + alpha * (reward + gamma * best_next_action - current_q_value)

# Reward function (e.g., based on distance and delivery time)
def calculate_reward(pickup_distance, delivery_time, max_time=50):
    if delivery_time <= max_time:
        return 100 - (pickup_distance / 1000)  # Positive reward for shorter distances and quick delivery
    else:
        return -100  # Penalty for exceeding time limit

start_time = time.time()
# Iterate over all orders
for order_index, order in order_data.iterrows():
    # print(f"Processing Order {order_index + 1}/{len(order_data)} (Order ID: {order['Order ID']})")
    
    # Get restaurant and delivery locations
    restaurant_lat = order['Restaurant Latitude']
    restaurant_lon = order['Restaurant Longitude']
    delivery_lat = order['Order Latitude']
    delivery_lon = order['Order Longitude']

    restaurant_node = get_nearest_node(restaurant_lat, restaurant_lon)
    delivery_node = get_nearest_node(delivery_lat, delivery_lon)

    # Get selected rider from the Q-table output of Model 1
    state = f"order_{order['Order ID']}"
    rider_index = max(Q_table_model_1[state], key=Q_table_model_1[state].get)
    rider_index = int(rider_index)  # Convert to integer if possible
    selected_rider = rider_data.iloc[rider_index]
    rider_node = get_nearest_node(selected_rider['Rider Latitude'], selected_rider['Rider Longitude'])

    # print(f"Selected Rider {selected_rider['Rider ID']} for Order {order['Order ID']}. Finding route...")

    # Calculate the route from rider to restaurant
    route_rider_to_restaurant = calculate_route(rider_node, restaurant_node)
    if route_rider_to_restaurant is None:
        print(f"No path found between Rider {selected_rider['Rider ID']} and Restaurant.")
        continue

    # Calculate the route from restaurant to delivery destination
    route_restaurant_to_delivery = calculate_route(restaurant_node, delivery_node)
    if route_restaurant_to_delivery is None:
        print(f"No path found between Restaurant and Delivery location.")
        continue

    # Track the total route
    total_route = route_rider_to_restaurant + route_restaurant_to_delivery
    # print(f"Route found for Order {order['Order ID']}. Total route length: {len(total_route)} nodes.")

    # Find additional orders within a certain radius along the route
    for idx, other_order in order_data.iterrows():
        if idx != order_index:
            other_delivery_node = get_nearest_node(other_order['Order Latitude'], other_order['Order Longitude'])
            if nx.shortest_path_length(G, source=restaurant_node, target=other_delivery_node, weight='length') <= SEARCH_RADIUS:
                
                # Select action using ε-greedy policy: Pick up or skip the nearby order
                state = f"order_{order['Order ID']}_additional_{other_order['Order ID']}"
                action = select_action(state, Q_table_model_2, epsilon)

                if action == 1:  # Pick up the additional order
                    # Calculate pickup distance and delivery time
                    pickup_distance = nx.shortest_path_length(G, source=restaurant_node, target=other_delivery_node, weight='length')
                    delivery_time = (pickup_distance / 1000) / 30 * 60  # Assuming speed is 30 km/h

                    # Calculate reward
                    reward = calculate_reward(pickup_distance, delivery_time)

                    # Update Q-table for this state-action pair
                    next_state = f"order_{increment_order_id(order['Order ID'])}" if order_index + 1 < len(order_data) else state
                    update_q_value(Q_table_model_2, state, action, reward, next_state, alpha, gamma)

                    # print(f"Picked up additional Order {other_order['Order ID']}. Distance: {pickup_distance:.2f} meters, Reward: {reward:.2f}")
                # else:
                    # print(f"Skipped additional Order {other_order['Order ID']}.")

    # Print progress and estimated remaining time
    elapsed_time = time.time() - start_time
    completed_orders = order_index + 1
    total_orders = len(order_data)
    remaining_orders = total_orders - completed_orders

    # Estimate time per order
    if completed_orders > 0:
        time_per_order = elapsed_time / completed_orders
    else:
        time_per_order = 0

    estimated_remaining_time = time_per_order * remaining_orders
    print(f"Completed processing Order {order['Order ID']}")
    print(f"Elapsed Time: {elapsed_time / 60:.2f} minutes")
    print(f"Estimated Remaining Time: {estimated_remaining_time / 60:.2f} minutes")
    print("-" * 50)

# Save the Q-table for Model 2
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

with open('q_table_model_2.json', 'w') as f:
    json.dump(default_to_regular(Q_table_model_2), f)

print("Model 2 training completed and Q-table saved.")