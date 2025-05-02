# Stock Oracle Group
# 4/9/2025
# Main control script for the stock oracle project
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import os
import pandas as pd

from graph import Graph
from fetch_stock_news import get_yahoo_finance_news
from urllib.request import urlopen, Request
from predictor import predict_tomorrow
from predictor import check_confidence
from fetch_stock_data import fetch_and_save_data

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,)

graph_instance = Graph(data=[])
app.layout = dbc.Container(fluid=True, children=[

    # Navbar
    dbc.NavbarSimple(
        brand="📈 Stock Oracle",
        brand_href="#",
        color="dark",
        dark=True,
    ),

    # Header
    dbc.Row(
        dbc.Col([
            html.H1("Price Prediction & Model Simulation", className="mt-4 mb-2"),
            html.H6("Tomorrow’s forecast, confidence intervals, and latest news", className="mb-4"),
        ]),
    ),

    # Body
    dbc.Row([

        # Left column: ticker + news
        dbc.Col(width=4, children=[
            dbc.Card([
                dbc.CardBody([
                    html.Label("Ticker Symbol"),
                    dcc.Input(id="ticker-input", placeholder="e.g. AAPL", className="form-control mb-2"),
                    dbc.Button("Load Data", id="load-real-data-btn", color="primary", className="mb-3"),

                    html.Div(id="news-container")
                ])
            ], className="mb-4")
        ]),

        # Right column: main graph + prediction
        dbc.Col(width=8, children=[
            dcc.Store(id='data-loaded-store', data=False),
            html.Div(id='price-prediction-section', children=[
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Historical Price", className="card-title"),
                        html.Div(id="graph-container"),
                        html.H5("Tomorrow's Prediction", className="mt-4"),
                        html.Div(id="prediction-container"),
                    ])
                ])
            ], style={'display': 'none'})
        ])
    ], className="mb-5"),

    dbc.Row([

        # Left column: days ahead + confidence
        dbc.Col(width=4, children=[
            dbc.Card([
                dbc.CardBody([
                    html.Label("Divergence Point (Days Behind Today)"),
                    dcc.Input(id="past-days-input", placeholder="Enter number of days", className="form-control mb-2"),
                    html.Label("Days Used in Predictions"),
                    dcc.Input(id="lag-days-input", placeholder="Enter number of days (Recommended: 5)", className="form-control mb-2"),
                    dbc.Button("Check Confidence", id="check-confidence-btn", color="secondary"),
                    html.Div(id="confidence-text", className="mt-3"),
                ])
            ])
        ]),

        # Right column: confidence graph
        dbc.Col(width=8, children=[
            html.Div(id="confidence-graph-container")
        ]),
    ]),

    # hidden interval to trigger news on page load
    dcc.Interval(id="news-interval", interval=1_000, n_intervals=0, max_intervals=1),

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
     Input("past-days-input", "n_submit")],
    [State("past-days-input", "value"),
     State("lag-days-input", "value")],
    prevent_initial_call=True
)
def check_confidence_callback(n_clicks, n_submit, days, lag_days):
    if not days:
        return "Please enter number of days.", "", ""

    if not os.path.exists("data.csv"):
        return "Load real data first.", "", ""

    # Validate inputs
    try:
        days = int(days)
        # Use half of days as default if lag_days not provided
        lag_days = int(lag_days) if lag_days else max(1, days // 2)
    except ValueError:
        return "Invalid input: Please enter valid numbers.", "", ""

    # Read data and generate predictions
    graph_instance.read_csv()
    prediction_text = f"Tomorrow's predicted closing value: {predict_tomorrow(graph_instance, lag_days):.2f}"

    try:
        confidence, prediction_graph_instance = check_confidence(graph_instance, days, lag_days, return_graph=True)

        # Create visualization DataFrames
        data_predicted = pd.DataFrame(prediction_graph_instance.data, columns=['Date', 'Value'])
        data_real = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])

        figure = {
            "data": [
                {"x": data_predicted["Date"], "y": data_predicted["Value"], "type": "line", "name": "Predicted"},
                {"x": data_real["Date"], "y": data_real["Value"], "type": "line", "name": "Real"}
            ],
            "layout": {
                "title": f"Prediction for {days} days behind today (using {lag_days} lag days)",
                "showlegend": True
            }
        }

        return dcc.Graph(figure=figure), f"Confidence Interval: {confidence * 100:.2f}%", prediction_text

    except Exception as e:
        return f"Error generating predictions: {str(e)}", "", ""

# Callback for news updates
@app.callback(
    Output("news-container", "children"),
    Input("ticker-input", "value"),
    prevent_initial_call=True
)
def update_news(ticker):

    if not ticker:
        return html.P("Please enter a ticker symbol.")

    # Fetch news for the ticker
    news = get_yahoo_finance_news(ticker)

    # Turn the news into a Dash component
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

            sentiment = article.get('sentiment', 'Unknown')
            news_elements.append(html.Div([
                html.A(final_title, href=article['url'], target="_blank", style={"fontWeight": "bold"}),
                html.Span(f" - Sentiment: {sentiment}", style={"marginLeft": "10px", "color": "green" if sentiment == "Positive" else "red" if sentiment == "Negative" else "gray"}),
                       ], style={"display": "block", "marginBottom": "10px"})
            )
    else:
        news_elements.append(html.P(f"No news found for {ticker.upper()}."))

    return news_elements

# Callback for object visibility
@app.callback(
    Output('price-prediction-section', 'style'),
    [Input('load-real-data-btn', 'n_clicks')],
    [State('ticker-input', 'value')],
    prevent_initial_call=True
)
def toggle_price_section(n_clicks, ticker):
    if ticker and os.path.exists('data.csv'):
        return {'display': 'block'}

    return {'display': 'none'}


if __name__ == "__main__":
    app.run(debug=True)
