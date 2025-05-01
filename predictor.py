# Stock Oracle Group
# 4/30/2025
# File for the predictor function and related functions
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from graph import Graph

# how many prior days to use in our autoregressive model
LAG_DAYS = 30

def build_lagged_df(series: pd.Series, lags: int) -> pd.DataFrame:
    df = pd.DataFrame({'y': series})
    for i in range(1, lags + 1):
        df[f'lag_{i}'] = df['y'].shift(i)
    return df.dropna()

def predict_tomorrow(graph_instance: Graph) -> float:
    if not graph_instance.data:
        graph_instance.read_csv()

    # Convert graph data to DataFrame
    df = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    series = df['Value']

    # get the last lagged values
    lagged = build_lagged_df(series, LAG_DAYS)
    x = lagged[[f'lag_{i}' for i in range(1, LAG_DAYS+1)]].to_numpy()
    y = lagged['y'].to_numpy()

    # fit a linear regression model
    model = LinearRegression().fit(x, y)
    last_vals = series.iloc[-LAG_DAYS:].to_numpy().reshape(1, -1)

    return float(model.predict(last_vals)[0])

def predict_days_ahead(graph_instance: Graph, days: int) -> Graph:
    graph_instance.read_csv()
    full = list(graph_instance.data)
    n = len(full)

    # Make a new graph for the predictions
    days = max(1, min(days, n-1))
    predictions = Graph(data=list(full[: n - days ]))

    # Get start and end dates from original graph data
    origin_start = datetime.datetime.strptime(graph_instance.data[0][0], "%Y-%m-%d")
    origin_end = datetime.datetime.strptime(graph_instance.data[-1][0], "%Y-%m-%d")

    # Generate predictions until we reach or exceed the end date
    while True:
        last_date = predictions.data[-1][0]
        if isinstance(last_date, str):
            last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")

        if last_date >= origin_end:
            break

        val = predict_tomorrow(predictions)
        next_val = last_date + datetime.timedelta(days=1)
        predictions.data.append((next_val.strftime("%Y-%m-%d"), val))

    # Remove any predictions before the original start date
    predictions.data = [
        (date, value) for date, value in predictions.data
        if datetime.datetime.strptime(date, "%Y-%m-%d") >= origin_start
    ]

    return predictions

def check_confidence(graph_instance: Graph, days: int, return_graph=False):
    full_pred = predict_days_ahead(graph_instance, days)

    # Convert both graphs' data to pandas DataFrames
    pred_df = pd.DataFrame(full_pred.data, columns=['Date', 'Value'])
    real_df = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])

    # Chop off all but the last days of the data
    pred_df_tail = pred_df.tail(days)
    real_df_tail = real_df.tail(days)

    # Calculate areas under both curves using trapezoidal integration
    pred_area = np.trapezoid(pred_df_tail['Value'])
    real_area = np.trapezoid(real_df_tail['Value'])

    # Calculate confidence as 1 - normalized absolute difference between areas
    area_diff = abs(pred_area - real_area)
    max_area = max(pred_area, real_area)
    confidence = 1 - (area_diff / max_area)

    # Ensure confidence is between 0 and 1
    confidence = max(0.0, min(1.0, confidence))

    if return_graph:
        return confidence, full_pred

    return confidence
