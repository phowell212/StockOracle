# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
from dash import dcc, html, Input, Output, State
import os
import pandas as pd
import predictor
from graph import Graph
from fetch_stock_news import get_yahoo_finance_news
from urllib.request import urlopen, Request
from predictor import predict_tomorrow
from fetch_stock_data import fetch_and_save_data

# Initialize the Dash app
app = dash.Dash(__name__)

graph_instance = Graph(data=[])
app.layout = html.Div([

    # Header
    html.H1("Stock Oracle"),
    html.H2("Price prediction and model effectiveness simulation"),

    # Ticker input section
    html.Div([
        dcc.Input(
            id="ticker-input",
            type="text",
            placeholder="Enter ticker symbol",
            style={"marginRight": "10px"}
        ),
        html.Button("Load Real Data", id="load-real-data-btn"),
    ]),

    # Graph and prediction containers
    html.Div(id="graph-container"),
    html.Div(id="prediction-container"),

    # Confidence section
    html.Div([
        dcc.Input(
            id="days-input",
            type="text",
            placeholder="Enter number of days",
            style={"marginRight": "10px"}
        ),
        html.Button("Generate Prediction", id="check-confidence-btn"),
    ], style={"marginTop": "20px"}),

    # Confidence results
    html.Div(id="confidence-text", style={"marginTop": "10px"}),
    html.Div(id="confidence-graph-container", style={"marginTop": "20px"}),

    # News section
    html.Div(id="news-container"),
    dcc.Interval(id="news-interval", interval=1000, n_intervals=0, max_intervals=1)
])

# Callback for data fetching and graph generation
@app.callback(
    Output("graph-container", "children"),
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


# Callback for value prediction
@app.callback(
    [Output("confidence-graph-container", "children"),
     Output("confidence-text", "children"),
     Output("prediction-container", "children")],
    [Input("check-confidence-btn", "n_clicks"),
     Input("days-input", "n_submit")],
    [State("days-input", "value")],
    prevent_initial_call=True
)
def check_confidence_callback(n_clicks, n_submit, days):
    if not days:
        return "Please enter number of days.", "", ""

    try:
        days = int(days)
    except ValueError:
        return "Invalid input for number of days.", "", ""

    # Ensure the real data is loaded from CSV
    graph_instance.read_csv()

    # Get tomorrow's prediction
    prediction_text = f"Tomorrow's predicted closing value: {predict_tomorrow(graph_instance):.2f}"

    # Get confidence and prediction graph
    confidence, prediction_graph_instance = predictor.check_confidence(graph_instance, days, return_graph=True)

    # Create DataFrames for visualization
    data_predicted = pd.DataFrame(prediction_graph_instance.data, columns=['Date', 'Value'])
    data_real = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])

    figure = {
        "data": [
            {"x": data_predicted["Date"], "y": data_predicted["Value"], "type": "line", "name": "Predicted"},
            {"x": data_real["Date"], "y": data_real["Value"], "type": "line", "name": "Real"}
        ],
        "layout": {
            "title": f"Prediction for {days} days ahead",
            "showlegend": True
        }
    }

    graph_component = dcc.Graph(figure=figure)
    confidence_text = f"Confidence Interval: {confidence * 100:.2f}%"

    return graph_component, confidence_text, prediction_text


# Callback for news updates
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
            except Exception:
                final_title = "Error fetching title"
            news_elements.append(
                html.A(final_title, href=article['url'], target="_blank",
                       style={"display": "block", "marginBottom": "10px"})
            )
    else:
        news_elements.append(html.P(f"No news found for {ticker.upper()}."))
    return news_elements


if __name__ == "__main__":
    app.run(debug=True)