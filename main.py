# Stock Oracle Group
# 9/4/2025
# Main control script for the stock oracle project

import dash
import yfinance
import plotly
from dash import dcc

# Init the framework
app = dash.Dash(__name__)
app.layout = dash.html.Div([
    dash.html.H1("Stock Oracle"),
    dash.html.Div("This section tracks live data"),
    dcc.Input(id='ticker', type='text', placeholder='Enter Ticker Symbol', style={'marginRight': '10px'})
])

if __name__ == '__main__':
    app.run(debug=True)
