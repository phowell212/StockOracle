# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
from dash import dcc, html, Input, Output
import os
import pandas as pd
from graph import Graph

# Initialize the Dash app
app = dash.Dash(__name__)

# Create an instance of the Graph class
graph_instance = Graph(data=[])

# Define the layout
app.layout = html.Div([
    html.Button("Update Graph", id="update-graph-btn"),
    html.Button("Generate CSV Data", id="generate-csv-btn"),
    html.Button("Clear CSV File", id="clear-csv-btn"),
    html.Div(id="graph-container")  # Placeholder for the graph
])

# Callback to regenerate the CSV file
@app.callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("generate-csv-btn", "n_clicks"),
    prevent_initial_call=True
)
def regenerate_csv(n_clicks):
    graph_instance.generate_csv()
    return "CSV file regenerated. Click 'Update Graph' to display the graph."

# Callback to clear the CSV file
@app.callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("clear-csv-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_csv(n_clicks):
    graph_instance.clear_csv()
    return "CSV file cleared. Click 'Generate CSV Data' to create new data."

# Callback to update the graph
@app.callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("update-graph-btn", "n_clicks"),
    prevent_initial_call=True
)
def update_graph(n_clicks):
    if os.path.exists("data.csv"):
        graph_instance.read_csv()
        data = pd.read_csv("data.csv")
        figure = {
            "data": [
                {"x": data["Date"], "y": data["Value"], "type": "line", "name": "Value"}
            ],
            "layout": {"title": "Graph from CSV"}
        }
        return dcc.Graph(figure=figure)
    else:
        return "No CSV file found. Please generate the CSV file first."

if __name__ == "__main__":
    app.run(debug=True)
