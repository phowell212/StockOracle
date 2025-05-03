# Stock Oracle Group
# 4/30/2025
# File for the predicted graph functionality
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from graph import Graph

class PredictedGraph(Graph):
    """
       Extends the Graph class to support time-series forecasting using autoregressive linear regression.
       Enables prediction of future stock prices and evaluation of prediction accuracy.
    """
    def __init__(self, predictor=None, *args, **kwargs):
        """
            Initializes a PredictedGraph object with an optional predictor.

            Parameters:
                predictor (object): An object with a `predict_tomorrow(lag_days)` method.
        """
        super().__init__(*args, **kwargs)

        # Any predictor can be used as long as it has a predict_tomorrow method, equivalents must be mapped manually
        self.predictor = predictor

    @staticmethod
    def build_lagged_df(series: pd.Series, lags: int) -> pd.DataFrame:
        """
            Constructs a DataFrame of lagged variables for autoregressive modeling.

            Parameters:
                series (pd.Series): Time series data.
                lags (int): Number of lagged days to include.

            Returns:
                pd.DataFrame: DataFrame with lagged values.
        """
        # Build a DataFrame with lagged values for autoregression
        df = pd.DataFrame({'y': series})
        for i in range(1, lags + 1):
            df[f'lag_{i}'] = df['y'].shift(i)
        return df.dropna()

    def predict_tomorrow(self, lag_days: int) -> float:
        """
            Predicts the next day's stock value using linear regression on lagged values.

            Parameters:
                lag_days (int): Number of lag days to use as features.

            Returns:
                float: Predicted stock price for the next day.
        """
        # Predict the next day's value using a linear regression on lagged values
        if not self.data:
            self.read_csv()

        # Convert data to DataFrame and set up the series
        df = pd.DataFrame(self.data, columns=['Date', 'Value'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        series = df['Value']

        # Make the lagged DataFrame and prepare the data for regression
        lagged_df = self.build_lagged_df(series, lag_days)
        x = lagged_df[[f'lag_{i}' for i in range(1, lag_days + 1)]].to_numpy()
        y = lagged_df['y'].to_numpy()

        # Fit the linear regression model
        model = LinearRegression().fit(x, y)
        last_vals = series.iloc[-lag_days:].to_numpy().reshape(1, -1)
        return float(model.predict(last_vals)[0])

    def predict_days_ahead(self, days: int, lag_days: int) -> 'PredictedGraph':
        """
            Predicts stock prices for a number of days into the future using recursive prediction.

            Parameters:
                days (int): Number of days to predict ahead.
                lag_days (int): Number of lagged days to use in prediction.

            Returns:
                PredictedGraph: New instance with predicted data.
        """
        if not self.data:
            self.read_csv()

        full = list(self.data)
        n = len(full)
        days = max(1, min(days, n - 1))

        # Initialize a new PredictedGraph with the historical slice
        initial_data = full[: n - days]
        predictions = PredictedGraph(predictor=self.predictor, data=list(initial_data))

        # Get start and end dates from the original graph data
        origin_start = datetime.datetime.strptime(full[0][0], "%Y-%m-%d")
        origin_end   = datetime.datetime.strptime(full[-1][0], "%Y-%m-%d")

        # Generate predictions iteratively, feeding each new value back in
        while True:
            last_date = predictions.data[-1][0]
            if isinstance(last_date, str):
                last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")

            if last_date >= origin_end:
                break

            if self.predictor:
                next_value = self.predictor.predict_tomorrow(lag_days)
            else:
                next_value = predictions.predict_tomorrow(lag_days)

            next_date  = last_date + datetime.timedelta(days=1)
            predictions.data.append((next_date.strftime("%Y-%m-%d"), next_value))

        # Drop any entries before the original start date
        predictions.data = [
            (date, value) for date, value in predictions.data
            if datetime.datetime.strptime(date, "%Y-%m-%d") >= origin_start
        ]

        return predictions

    def check_confidence(self, days: int, lag_days: int, return_graph=False):
        """
            Evaluates how closely the predicted values match actual values using area under the curve comparison.

            Parameters:
                days (int): Number of days to use for comparison.
                lag_days (int): Lag days used in prediction.
                return_graph (bool): If True, also returns the predicted graph.

            Returns:
                float: Confidence score between 0.0 and 1.0.
                PredictedGraph (optional): The predicted graph object (if return_graph is True).
        """
        # Get the Dataframes for numpy trapezoid integration
        full_pred = self.predict_days_ahead(days, lag_days)
        pred_df = pd.DataFrame(full_pred.data, columns=['Date', 'Value'])
        real_df = pd.DataFrame(self.data,      columns=['Date', 'Value'])

        # Chop off the last n days from both DataFrames and save them
        pred_tail = pred_df.tail(days)
        real_tail = real_df.tail(days)

        # Use the tails to calculate the confidence
        pred_area = np.trapz(pred_tail['Value'])
        real_area = np.trapz(real_tail['Value'])
        area_diff = abs(pred_area - real_area)
        max_area  = max(pred_area, real_area)
        confidence = 1 - (area_diff / max_area) if max_area != 0 else 0.0
        confidence = max(0.0, min(1.0, confidence))

        # Return the graph if requested
        if return_graph:
            return confidence, full_pred
        return confidence
