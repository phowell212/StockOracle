# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
from dash import dcc, html, Input, Output, State
import os
import pandas as pd
import predictor
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
    [Input("load-real-data-btn", "n_clicks"),
     Input("ticker-input", "n_submit")],
    State("ticker-input", "value"),
    prevent_initial_call=True
)
def load_real_data(n_clicks, n_submit, ticker):
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

# Callback to fetch and display news as clickable links using the extracted titles
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
            try:
                req = Request(article['url'], headers=headers)
                page = urlopen(req)
                html_content = page.read().decode("utf-8")
                title_index = html_content.find("<title>") + len("<title>")
                end_index = html_content.find("</title")
                final_title = html_content[title_index: end_index]
            except Exception as e:
                final_title = "Error fetching title"
            news_elements.append(
                html.A(final_title, href=article['url'], target="_blank", style={"display": "block", "marginBottom": "10px"})
            )
    else:
        news_elements.append(html.P(f"No news found for {ticker.upper()}."))
    return news_elements

# Extend the app layout with an input for number of days and separate containers for graph and text.
app.layout = html.Div([
    dcc.Input(
        id="ticker-input",
        type="text",
        placeholder="Enter ticker symbol",
        style={"marginRight": "10px"}
    ),
    html.Button("Load Real Data", id="load-real-data-btn"),
    html.Button("Predict Tomorrow's Value", id="predict-btn"),
    html.Div(id="graph-container"),  # existing graph container
    html.Div(id="prediction-container"),  # existing prediction container
    dcc.Input(
        id="days-input",
        type="text",
        placeholder="Enter number of days",
        style={"marginTop": "20px", "marginRight": "10px"}
    ),
    html.Div(id="confidence-text", style={"marginTop": "10px"}),
    html.Div(id="confidence-graph-container", style={"marginTop": "20px"}),
    html.Div(id="news-container"),  # news container remains the same
    dcc.Interval(id="news-interval", interval=1000, n_intervals=0, max_intervals=1)
])


# Callback to check prediction confidence over a number of days.
@app.callback(
    [Output("confidence-graph-container", "children"),
     Output("confidence-text", "children")],
    Input("days-input", "n_submit"),
    State("days-input", "value"),
    prevent_initial_call=True
)
def check_confidence_callback(n_submit, days):
    try:
        days = int(days)
    except Exception:
        return "Invalid input for number of days.", ""

    if not os.path.exists("data.csv"):
        return "Load real data first.", ""

    # Ensure the real data is loaded from CSV.
    graph_instance.read_csv()

    # Create a builder graph and check the confidence.
    confidence, prediction_graph_instance = predictor.check_confidence(graph_instance, days, return_graph=True)

    # Make a figure with the two graphs overlayed on top of each other.
    data_predicted = pd.DataFrame(prediction_graph_instance.data, columns=['Date', 'Value'])
    data_real = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])
    figure = {
        "data": [
            {"x": data_predicted["Date"], "y": data_predicted["Value"], "type": "line", "name": "Predicted"},
            {"x": data_real["Date"], "y": data_real["Value"], "type": "line", "name": "Real"}
        ],
        "layout": {"title": f"Confidence for {days} days ahead"}
    }

    graph_component = dcc.Graph(figure=figure)
    confidence_text = f"Confidence Interval: {confidence * 100:.2f}%"
    return graph_component, confidence_text

if __name__ == "__main__":
    app.run(debug=True)