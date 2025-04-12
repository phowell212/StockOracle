# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
from dash import dcc, html, Input, Output
import os
import pandas as pd
from graph import Graph
from newsFetcher import get_yahoo_finance_news
from urllib.request import urlopen, Request
from predictor import predict_tomorrow
from generate_data import fetch_and_save_data  # New import for real data

# Initialize the Dash app
app = dash.Dash(__name__)

graph_instance = Graph(data=[])

app.layout = html.Div([
    html.Button("Update Graph", id="update-graph-btn"),
    html.Button("Generate CSV Data", id="generate-csv-btn"),
    html.Button("Clear CSV File", id="clear-csv-btn"),
    html.Button("Predict Tomorrow's Value", id="predict-btn"),
    html.Button("Load Real Stock Data", id="load-real-data-btn"),  # New button
    html.Div(id="graph-container"),  # Placeholder for the graph
    html.Div(id="prediction-container"),  # Placeholder for the prediction
    html.Div(id="news-container"),  # Placeholder for news
    dcc.Interval(id="news-interval", interval=1000, n_intervals=0, max_intervals=1)
])

# Callback to regenerate CSV data using generated fake data
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

# Callback to generate prediction for tomorrow's value
@app.callback(
    Output("prediction-container", "children"),
    Input("predict-btn", "n_clicks"),
    prevent_initial_call=True
)
def predict_value(n_clicks):
    if os.path.exists("data.csv"):
        graph_instance.read_csv()
        prediction = predict_tomorrow(graph_instance)
        return f"Tomorrow's predicted closing value: {prediction:.2f}"
    return "No CSV file found. Generate data first."

# Callback to load real stock data using generate_data.py
@app.callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("load-real-data-btn", "n_clicks"),
    prevent_initial_call=True
)
def load_real_data(n_clicks):
    ticker = "AAPL"
    fetch_and_save_data(ticker, "data.csv")
    return "Real stock data loaded. Click 'Update Graph' to display the graph."

# Callback to fetch and display news
@app.callback(
    Output("news-container", "children"),
    Input("news-interval", "n_intervals")
)
def update_news(n_intervals):
    if n_intervals == 0:
        return dash.no_update

    symbol = "AAPL"
    news = get_yahoo_finance_news(symbol)
    news_elements = []

    if news:
        news_elements.append(html.H3(f"News for {symbol}:"))
        news_elements.append(html.Hr())
        for article in news:
            news_elements.append(html.P(f"Article Name: {article['title']}"))
            news_elements.append(html.P(f"Link: {article['url']}"))
    else:
        news_elements.append(html.P(f"No news found for {symbol}."))

    headers = {'User-Agent': 'Mozilla/5.0'}
    for article in news:
        try:
            req = Request(article['url'], headers=headers)
            page = urlopen(req)
            url_content = page.read()
            html_content = url_content.decode("utf-8")
            title_index = html_content.find("<title>") + len("<title>")
            end_index = html_content.find("</title")
            final_title = html_content[title_index:end_index]
            news_elements.append(html.P(f"Extracted Title: {final_title}"))
        except Exception as e:
            news_elements.append(html.P(f"Error fetching {article['url']}: {e}"))

    return news_elements

if __name__ == "__main__":
    app.run(debug=True)
