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

])


if __name__ == '__main__':
    app.run(debug=True)
