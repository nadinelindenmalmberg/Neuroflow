import requests
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, url_for
import plotly
import plotly.graph_objects as go
import json
from utils.normalize import normalize_values
from flask_sqlalchemy import SQLAlchemy
from models import db, Graph, DataPoint
from flask_migrate import Migrate
from datetime import datetime

mock_data = [
    {"metric_name": "Revenue", "date": datetime.date(2024, 1, 10)},
    {"metric_name": "Profit", "date": datetime.date(2024, 1, 5)},
    {"metric_name": "Expenses", "date": datetime.date(2024, 1, 12)},
]

sorted_data = sorted(mock_data, key=lambda dp: (dp['metric_name'], dp['date']))
print(sorted_data)



# Dummy classes to simulate your setup
class DataPoint:
    def __init__(self, date, metric_name, value):
        self.date = date
        self.metric_name = metric_name
        self.value = value

class Graph:
    def __init__(self, name):
        self.name = name
        self.data_points = []

# Create a dummy Graph object
dummy_graph = Graph(name="Test Graph")

# Add dummy data points
dummy_graph.data_points = [
    DataPoint(datetime(2025, 1, 1), "Metric A", 10),
    DataPoint(datetime(2025, 1, 2), "Metric A", 15),
    DataPoint(datetime(2025, 1, 3), "Metric A", 12),
    DataPoint(datetime(2025, 1, 1), "Metric B", 20),
    DataPoint(datetime(2025, 1, 2), "Metric B", 25),
    DataPoint(datetime(2025, 1, 3), "Metric B", 23),
    DataPoint(datetime(2025, 1, 1), "Metric C", 5),
    DataPoint(datetime(2025, 1, 2), "Metric C", 7),
    DataPoint(datetime(2025, 1, 3), "Metric C", 6),
]

def create_plot_for_graph(graph_obj):
    points = sorted(graph_obj.data_points, key=lambda dp: (dp.metric_name, dp.date)) # 1. Sort data points by (metric_name, date) so each metric’s data is chronological
    if not points:
        return None
    
    print(points)

    fig = go.Figure() #creates the empty plot

    #2. Group data points by metric_name using a dictionary.

    metrics_data = {} #initializes empty object of metrics_data
    for dp in points: 
        metric = dp.metric_name
        if metric not in metrics_data:
            metrics_data[metric] = {"x": [], "y": []}
        metrics_data[metric]["x"].append(dp.date)
        metrics_data[metric]["y"].append(dp.value)
    
    print(metrics_data)

    # 3. Add a separate trace for each metric_name.
    for metric, data in metrics_data.items():
        fig.add_trace(
            go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="lines+markers",
                name=metric  # <--- show metric name in the legend
            )
        )

    fig.update_layout(
        title=graph_obj.name,
        xaxis_title="Date",
        yaxis_title="Value"
    )
    return 1
    # Convert to a JSON-friendly dict for Plotly
    ##return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


plot_data = create_plot_for_graph(dummy_graph)
print(plot_data)


def testing(): 
    list = ["banana", "apple", "orange"]
    str_list = []
    for item in list: 
        str_list.append(item)
    return " ".join(str_list)

print(testing())


#challenge 1 - sorting

from datetime import datetime

data_points = [
    {"metric": "heart_rate", "date": datetime(2025, 1, 10)},
    {"metric": "sleep", "date": datetime(2025, 1, 8)},
    {"metric": "heart_rate", "date": datetime(2025, 1, 5)},
    {"metric": "sleep", "date": datetime(2025, 1, 12)}
]

def sort_data_points(data_points): 
    data_points.sort(key=lambda x: (x["metric"], x["date"]))
    return data_points

print(sort_data_points(data_points))

multiply_by_two = lambda x: x*2

print(multiply_by_two(2))


from datetime import datetime

d = datetime(2025, 1, 15)
# Expected output: "2025-01-15"

def format_date(date): 
    string_date = date.strftime("%Y-%m-%d")
    return string_date

print(format_date(d))

#challenge #3 - Given a list of data points (as dictionaries with keys "metric", "date", and "value"), 
# write a function group_by_metric(data_points) that returns a dictionary where each key is a metric name and the value 
# is a list of data points (the dictionaries) for that metric.

data_points = [
    {"metric": "heart_rate", "date": "2025-01-10", "value": 70},
    {"metric": "sleep", "date": "2025-01-08", "value": 7.5},
    {"metric": "heart_rate", "date": "2025-01-05", "value": 68},
    {"metric": "sleep", "date": "2025-01-12", "value": 6.8}
]

def group_by_metric(data):
    new_dict = {}
    for item in data: 
        if item["metric"] not in new_dict: 
            new_dict.update({item["metric"]: []})
        new_dict[item["metric"]].append(item["value"])
    
    return new_dict

print(group_by_metric(data_points))


list = []
list.append(1)
print(list)

#challenge 4: 

from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("MY_SECRET")
print(key)

#challenge 5: 
numbers = [1, 2, 3, 4]

def squared_them (numbers): 
	return [item * item for item in numbers]

print(squared_them(numbers))

names = ['daniel', 'gustav', 'victor']

def evaluate_daniel (names): 
    return {name: "is a shit" for name in names}

print(evaluate_daniel(names))

#Challenge 6: Filter and Transform Numbers
numbers = [1, 2, 3, 4, 5]

def triple (numbers): 
    return [item * 2 if item % 2 == 0 else item * 3 for item in numbers]

print(triple(numbers))

#Challenge 7: Extract Unique Words from a Sentence
sentence = "Hello, world! Hello Python."

def extract_words (sentence): 
    for char in ",.!":
        sentence = sentence.replace(char, "")
    final = sentence.lower().split(" ")
    print(f'final {final}')

    my_set = set(final)
    return my_set

print(extract_words(sentence))

#challenge 8

nested_list = [[1, 2, 3], [4, 5], [6, 7, 8]]

def flatten (nested_list): 
    flattened = []
    for array in nested_list: 
        for number in array: 
            flattened.append(number)
    return flattened

print(flatten(nested_list))

nested_list = [[1, 2, 3], [4, 5], [6, 7, 8]]

def flatten_comprehension (nested_list):
    return [number for array in nested_list for number in array]

print(flatten_comprehension(nested_list))

#challenge 9: 

def find_number(numbers):
    count_dict = {}

    # Count occurrences
    for num in numbers:
        count_dict[num] = count_dict.get(num, 0) + 1

    print(count_dict)

    # Find the most frequent number
    most_frequent = max(count_dict, key=count_dict.get)  
    return most_frequent

numbers = [1, 3, 2, 1, 4, 1, 3, 3, 3, 3, 2]
print(find_number(numbers))  # Output: 3


my_other_dict = {}

my_other_dict["value"] = 0

print(my_other_dict.get["value"])


#understanding the database better: 

from app import app, db
from dotenv import load_dotenv
import os
from models import db, Graph, DataPoint
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://***REMOVED***:***REMOVED***@***REMOVED***:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

with app.app_context():
    graphs = db.session.query(Graph).filter_by(is_temporary=True).all()
    print(graphs)