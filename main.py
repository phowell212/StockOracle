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

graph_instance = Graph(data=[])

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


#Author: Praneeth Sai Ummadisetty
# Date: 04-08-2025
# Description: This is the main class for getting the articles from the web using scraping methods
from newsFetcher import get_yahoo_finance_news
from urllib.request import urlopen, Request

symbol = "AAPL"
news = get_yahoo_finance_news(symbol)
if news:
    print(f"\n News for {symbol}:")
    print("-" * 40)
    for article in news:
        print(f"Article Name: {article['title']}\nLink: {article['url']}\n")
else:
    print(f"No news found for {symbol}.")

headers = {'User-Agent': 'Mozilla/5.0'}
for article in news:
    try:
        req = Request(article['url'], headers=headers)
        page = urlopen(req)
        print(page)
        url_Content = page.read()
        # print(url_Content[:500])
        html = url_Content.decode("utf-8")
        title = html.find("<title>") + len("<title>")
        endTitle = html.find("</title")
        print(title,endTitle)
        finalTitle = html[title:endTitle]
        print(finalTitle)
    except Exception as e:
        print(f"Error fetching {article['url']}: {e}")

if __name__ == "__main__":
    app.run(debug=True)
