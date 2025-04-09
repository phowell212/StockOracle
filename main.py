# Stock Oracle Group
# 9/4/2025
# Main control script for the stock oracle project

import yfinance
import plotly
import dash
from dash import dcc, html, Input, Output, State

# Init the framework
app = dash.Dash(__name__)
app.layout = html.Div([

    # input
    html.H1("Stock Oracle"),
    html.Div("This section tracks live data"),
    dcc.Input(id='ticker', type='text', placeholder='Enter Ticker Symbol', style={'marginRight': '10px'}),
    html.Button('Update', id='update-button', n_clicks=0, style={'marginTop': '10px'}),

    # graph (output)
    html.Div(id='live-graph', style={'width': '100%', 'height': '100vh'}),
    dcc.Graph(id='graph', style={'width': '100%', 'height': '100vh'}),

])


@app.callback(
    Output('graph', 'figure'),
    Input('update-button', 'n_clicks'),
    State('ticker', 'value')
)
def update_graph(n_clicks, ticker):
    if n_clicks > 0 and ticker:
        # Fetch data from Yahoo Finance
        data = yfinance.download(ticker, period='1d', interval='1m')
        fig = {
            'data': [
                {'x': data.index, 'y': data['Close'], 'type': 'line', 'name': ticker}
            ],
            'layout': {
                'title': f'Live Stock Data for {ticker}',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Price'},
            }
        }
        return fig
    else:
        return {'data': [], 'layout': {}}


if __name__ == '__main__':
    app.run(debug=True)
