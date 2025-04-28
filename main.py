# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
from dash import dcc, html, Input, Output, State
import os
import pandas as pd
from graph import Graph
from newsFetcher import get_yahoo_finance_news
from urllib.request import urlopen, Request
from predictor import predict_tomorrow
from generate_data import fetch_and_save_data

# Initialize the Dash app
app = dash.Dash(__name__)

graph_instance = Graph(data=[])

app.layout = html.Div([
    dcc.Input(
        id="ticker-input",
        type="text",
        placeholder="Enter ticker symbol",
        style={"marginRight": "10px"}
    ),
    html.Button("Load Real Data", id="load-real-data-btn"),
    html.Button("Predict Tomorrow's Value", id="predict-btn"),
    html.Div(id="graph-container"),  # Placeholder for the graph
    html.Div(id="prediction-container"),  # Placeholder for the prediction
    html.Div(id="news-container"),  # Placeholder for news
    dcc.Interval(id="news-interval", interval=1000, n_intervals=0, max_intervals=1)
])

# Callback to load real stock data using ticker input, update CSV and display graph
@app.callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("load-real-data-btn", "n_clicks"),
    State("ticker-input", "value"),
    prevent_initial_call=True
)
def load_real_data(n_clicks, ticker):
    ticker = ticker if ticker else "AAPL"
    fetch_and_save_data(ticker, "data.csv")
    if os.path.exists("data.csv"):
        graph_instance.read_csv()
        data = pd.read_csv("data.csv")
        figure = {
            "data": [{"x": data["Date"], "y": data["Value"], "type": "line", "name": "Value"}],
            "layout": {"title": f"Graph for {ticker.upper()}"}
        }
        return dcc.Graph(figure=figure)
    return "No CSV file found. Please try again."

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
    return "No CSV file found. Load data first."

# Callback to fetch and display news based on ticker input change with formatted extracted titles
@app.callback(
    Output("news-container", "children"),
    Input("ticker-input", "value"),
    prevent_initial_call=True
)
def update_news(ticker):
    ticker = ticker if ticker else "AAPL"
    news = get_yahoo_finance_news(ticker)
    news_elements = []
    if news:
        news_elements.append(html.H3(f"News for {ticker.upper()}:"))
        news_elements.append(html.Hr())
        headers = {'User-Agent': 'Mozilla/5.0'}
        for article in news:
            news_elements.append(html.P(f"Link: {article['url']}"))
            try:
                req = Request(article['url'], headers=headers)
                page = urlopen(req)
                html_content = page.read().decode("utf-8")
                title_index = html_content.find("<title>") + len("<title>")
                end_index = html_content.find("</title")
                final_title = html_content[title_index: end_index]
                news_elements.append(html.P(f"Extracted Title: {final_title}"))
            except Exception as e:
                news_elements.append(html.P(f"Error fetching {article['url']}: {e}"))
    else:
        news_elements.append(html.P(f"No news found for {ticker.upper()}."))
    return news_elements

if __name__ == "__main__":
    app.run(debug=True)