from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import pickle
import networkx as nx
import osmnx as ox
from collections import defaultdict
import random
import numpy as np
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the saved Bangalore map
with open('bangalore_graph.pkl', 'rb') as f:
    G = pickle.load(f)

# Load Q-tables
with open('q_table_model_1.json', 'r') as f:
    Q_table_model_1 = json.load(f)

with open('q_table_model_2.json', 'r') as f:
    Q_table_model_2 = json.load(f)

# Convert Q-tables to defaultdict
Q_table_model_1 = defaultdict(lambda: defaultdict(float), Q_table_model_1)
Q_table_model_2 = defaultdict(lambda: defaultdict(float), Q_table_model_2)

def get_nearest_node(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return ox.distance.nearest_nodes(G, X=[lon], Y=[lat])[0]
    except ValueError:
        return None

def calculate_route(source_node, target_node):
    try:
        return nx.shortest_path(G, source=source_node, target=target_node, weight='length')
    except nx.NetworkXNoPath:
        return None

def select_rider(state, available_riders, Q_table):
    state_actions = Q_table[state]
    return max(available_riders.index, key=lambda r: state_actions[str(r)])

def select_additional_order(state, Q_table):
    return max(Q_table[state], key=Q_table[state].get)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        app.logger.info("Processing data...")
        # Get order and rider data from the request
        order_data = pd.DataFrame(request.json['orderData'])
        rider_data = pd.DataFrame(request.json['riderData'])

        app.logger.info(f"Received {len(order_data)} orders and {len(rider_data)} riders")

        # Convert columns to appropriate types
        for col in ['Order Latitude', 'Order Longitude', 'Restaurant Latitude', 'Restaurant Longitude']:
            order_data[col] = pd.to_numeric(order_data[col], errors='coerce')

        for col in ['Rider Latitude', 'Rider Longitude']:
            rider_data[col] = pd.to_numeric(rider_data[col], errors='coerce')

        results = []

        for _, order in order_data.iterrows():
            app.logger.info(f"Processing order {order['Order ID']}")
            restaurant_node = get_nearest_node(order['Restaurant Latitude'], order['Restaurant Longitude'])
            delivery_node = get_nearest_node(order['Order Latitude'], order['Order Longitude'])

            if restaurant_node is None or delivery_node is None:
                app.logger.warning(f"Invalid nodes for order {order['Order ID']}")
                continue

            # Select rider using Model 1
            state = f"order_{order['Order ID']}"
            available_riders = rider_data[rider_data['Availability'] == 1]
            if available_riders.empty:
                app.logger.warning(f"No available riders for order {order['Order ID']}")
                continue
            rider_index = select_rider(state, available_riders, Q_table_model_1)
            selected_rider = available_riders.iloc[rider_index]
            rider_node = get_nearest_node(selected_rider['Rider Latitude'], selected_rider['Rider Longitude'])

            if rider_node is None:
                app.logger.warning(f"Invalid rider node for order {order['Order ID']}")
                continue

            # Calculate routes
            route_to_restaurant = calculate_route(rider_node, restaurant_node)
            route_to_delivery = calculate_route(restaurant_node, delivery_node)

            if route_to_restaurant is None or route_to_delivery is None:
                app.logger.warning(f"No valid route found for order {order['Order ID']}")
                continue

            total_route = route_to_restaurant + route_to_delivery
            total_distance = sum(ox.utils_graph.get_route_edge_attributes(G, total_route, 'length'))
            total_time = (total_distance / 1000) / 30 * 60  # Assuming 30 km/h speed

            additional_orders = []

            # Find additional orders using Model 2
            for _, other_order in order_data.iterrows():
                if other_order['Order ID'] != order['Order ID']:
                    other_delivery_node = get_nearest_node(other_order['Order Latitude'], other_order['Order Longitude'])
                    if other_delivery_node is not None:
                        if nx.shortest_path_length(G, source=restaurant_node, target=other_delivery_node, weight='length') <= 1000:
                            state = f"order_{order['Order ID']}_additional_{other_order['Order ID']}"
                            action = select_additional_order(state, Q_table_model_2)
                            if action == 1:
                                additional_orders.append(other_order['Order ID'])

            results.append({
                'order_id': order['Order ID'],
                'rider_id': selected_rider['Rider ID'],
                'total_distance': total_distance,
                'total_time': total_time,
                'fuel_consumption': total_distance / 25000,  # km/L
                'additional_orders': additional_orders,
                'route': [[G.nodes[node]['y'], G.nodes[node]['x']] for node in total_route]
            })

        app.logger.info(f"Processing complete. Generated {len(results)} results.")
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)