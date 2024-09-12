# BangaloreBytes (Maximizing profits, minimizing costs: The BangaloreBytes advantage for delivery businesses)

## Overview:
Create a RL based model for delivery startups to optimize the delivery system with dynamic parameter. The goal here is to delivery all the orders with minimum fuel consumption using minimum number of riders to deliver it at the promised time.

This problem first observed when me and my friend ordered the same food from a same restaurant at same time but from different accounts. Both the orders where delivered by 2 separate riders and on different time. This problem occurred many time and with different platforms as well that showcase the lack of optimum management in the rider scheduling problem in such companies.

The primary goal in delivery services is to deliver on time so we have to optimize the process without exceeding the time limit. We will be targeting efficient delivery within 50 minutes using least number of riders to deliver the orders and in a way that can save maximum fuel

## Data:
For dataset we have to gather a lot of orders data and riders informations as well, after going through many pre existing datasets we have decided to generate our own. First we have selected an location where we will be doing our deliveries so we have chosen "Bangalore" for that. We took the coordinates of the center location in Bangalore and decided to take 5 to 10 km radius map to perform our operations. We have created 2 separate files ordes_data and rider_data.

### Rider_data:
| Columns          | Description
|----------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Rider ID         | Unique id to identify different riders
| Rider Latitude   | Latitude of the riders primary location
| Rider Longitude  | Longitude of the riders primary location
| Availability   | Some riders may not be available due to different reason
| Capacity   | It tells us if rider is already carrying something and also how much weight we can give him

### Order_data:
| Columns          | Description
|----------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Order ID         | Unique id to identify different orders
| Order Latitude   | Latitude of the delivery location
| Order Longitude  | Longitude of the delivery location
| Restaurant Latitude   | Latitude of the restaurant location
| Restaurant Longitude   | Longitude of the restaurant location
| Timestamp   | Time at which order is placed, we will deliver our order within 50 mins of this
| Order Size   | Weight of the order
| Priority   | Some delivery service offers different priority depending if someone is their premium customer or not
| Traffic   | Traffic details around the area. This is the 'int' value where 1=low, 2=medium and 3=high
| Weather   | As this will affect the delivery timing, we have considered 'clear', 'rainy', 'foggy' and 'cloudy' days
| Time of Day   | This helps in deciding factors related to routes

## Approach
We will make 2 models based on the Q-learning, right now condition of the data is like this: First we have to choose a rider then the rider will travel to the restaurant and from the restaurant the rider will go the delivery location. Our first model will find the nearest rider that is available around the restaurant, in future we are planing to consider other parameter like weight of the rider to select the optimum rider. The first model will find the rider for the order and save its results. The model 2 will use this results and will use this rider for delivering the order. Now our second model we are considering that the rider has reached the restaurant so now the model 2 has to find all the possible routes between restaurant and the delivery location. From all the routes we will look for the route from which the rider can deliver maximum number of order but we will not neglect the order timing as we have to deliver original order with time limit. Our second model will give us the details of all the orders that the perticular rider will deliver.

## Evaluation Metrics
There are 3 evaluation metrics: Fuel Consumption, Total Travel Time and Number of Riders Involved. The fuel consumption will comes from the distance that we traveled, we have taken the average of '25' (we will burn 1 liter of fuel for 25 Km), the total time is the time taken by the rider to travel from its primary location to the restaurant and than from the restaurant to the delivery location. The number of riders involved would be the number of riders that we used to deliver all the orders.

## Contributions
At the heart of this project, we recognize the immense potential for growth through collaboration. Our goal to optimise our algorithm to achieve best possible results. We welcome all contributions!
