import pickle
import networkx as nx
import osmnx as ox
import pandas as pd
import numpy as np
import random
from collections import defaultdict
import json
import re

# Load the saved Bangalore map
with open('bangalore_graph.pkl', 'rb') as f:
    G = pickle.load(f)

# Load rider data and order data
rider_data = pd.read_csv('rider_data.csv')
order_data = pd.read_csv('order_data.csv')

# Parameters for Q-learning
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate

# Initialize Q-table as a nested defaultdict
Q_table = defaultdict(lambda: defaultdict(float))

# Reward function
def calculate_reward(distance, travel_time, max_time=50):
    if travel_time <= max_time:
        return max(0, 100 - (distance / 1000))
    else:
        return -(travel_time - max_time) * 10

# Function to get the nearest node in the graph
def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, X=lon, Y=lat)

# Function to select an action (rider) using ε-greedy policy
def select_rider(state, available_riders, Q_table, epsilon):
    if random.uniform(0, 1) < epsilon:  # Exploration
        return random.choice(available_riders.index)
    else:  # Exploitation
        state_actions = Q_table[state]
        return max(available_riders.index, key=lambda r: state_actions[r])

# Function to update Q-values
def update_q_value(Q_table, state, action, reward, next_state, alpha, gamma):
    best_next_action = max(Q_table[next_state].values()) if Q_table[next_state] else 0
    current_q_value = Q_table[state][action]
    Q_table[state][action] = current_q_value + alpha * (reward + gamma * best_next_action - current_q_value)

# Function to increment order ID
def increment_order_id(order_id):
    try:
        prefix = re.match(r'^([A-Za-z]+)', order_id).group(1)
        number = int(re.search(r'\d+', order_id).group())
        return f"{prefix}{number + 1:05d}"
    except AttributeError:
        print(f"Error with Order ID format: {order_id}")
        return order_id

# Iterate over all orders (states)
for order_index, order in order_data.iterrows():
    restaurant_lat = order['Restaurant Latitude']
    restaurant_lon = order['Restaurant Longitude']
    restaurant_node = get_nearest_node(restaurant_lat, restaurant_lon)
    
    # Get available riders
    available_riders = rider_data[rider_data['Availability'] == 1]
    
    if len(available_riders) == 0:
        print(f"No available riders for Order {order['Order ID']}.")
        continue
    
    # Select a rider (action) using the ε-greedy policy
    state = f"order_{order['Order ID']}"
    rider_index = select_rider(state, available_riders, Q_table, epsilon)
    selected_rider = available_riders.iloc[rider_index]
    rider_node = get_nearest_node(selected_rider['Rider Latitude'], selected_rider['Rider Longitude'])
    
    try:
        # Calculate the distance and travel time between rider and restaurant
        distance = nx.shortest_path_length(G, source=rider_node, target=restaurant_node, weight='length')
        travel_time = (distance / 1000) / 30 * 60  # Assume speed is 30 km/h
        
        # Calculate reward
        reward = calculate_reward(distance, travel_time)
        
        # Update Q-value for this state-action pair
        next_order_id = increment_order_id(order['Order ID']) if order_index + 1 < len(order_data) else order['Order ID']
        next_state = f"order_{next_order_id}"
        update_q_value(Q_table, state, rider_index, reward, next_state, alpha, gamma)
        
        print(f"Order {order['Order ID']}: Nearest rider is {selected_rider['Rider ID']}. Distance: {distance:.2f} meters, Travel Time: {travel_time:.2f} minutes, Reward: {reward:.2f}")
    
    except nx.NetworkXNoPath:
        print(f"No path found for Order {order['Order ID']} to Rider {selected_rider['Rider ID']}.")

# Save the Q-table for future use
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

with open('q_table_model_1.json', 'w') as f:
    json.dump(default_to_regular(Q_table), f)

print("Model 1 training completed and Q-table saved.")