# Stock Oracle Group
# 4/30/2025
# File for the predicted graph functionality
import numpy as np
import pandas as pd
from graph import Graph

class PredictedGraph(Graph):
    """
    Forecast using an AR model fitted on real data, then backtest simulate tail predictions.
    """

    def __init__(self, predictor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predictor = predictor

    def predict_tomorrow(self, lag_days: int, base_date: str = None) -> float:
        """
        Fit an AR(lag_days) model on data up to `base_date` and predict the next point.

        Parameters:
            lag_days   Number of past days to use as features.
            base_date  YYYY-MM-DD string to cutoff training data (inclusive). If None, use all data.

        Returns:
            float     Forecasted value for the day after base_date.
        """
        if not self.data:
            self.read_csv()

        # Build DataFrame and filter by base_date
        df = pd.DataFrame(self.data, columns=["Date", "Value"])
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values("Date", inplace=True)
        df.set_index("Date", inplace=True)

        if base_date:
            cutoff = pd.to_datetime(base_date)
            df = df.loc[:cutoff]

        series = df["Value"].to_numpy()
        n = series.size
        if n <= lag_days:
            raise ValueError(f"Need at least {lag_days+1} points; got {n}.")

        # Build lagged matrix X of shape (n-lag_days, lag_days)
        X = np.column_stack([
            series[i : n - lag_days + i]
            for i in range(lag_days)
        ])
        y = series[lag_days:]

        # Solve for AR coefficients via least squares
        coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)

        # Last lag_days values (most recent) for prediction
        window = series[-lag_days:][::-1]
        return float(np.dot(coeffs, window))

    def predict_days_ahead(self, days: int, lag_days: int) -> 'PredictedGraph':
        """
        Backtest: for the final `days` timepoints in self.data, predict each one using only real history.

        Parameters:
            days     Number of points at the end to forecast.
            lag_days Number of lags for the AR model.

        Returns:
            PredictedGraph containing historical data up to divergence and predicted tail.
        """
        if not self.data:
            self.read_csv()

        full = list(self.data)
        n = len(full)
        days = max(1, min(days, n - 1))

        # Historical segment up to the divergence point
        hist = full[: n - days]
        pg = PredictedGraph(predictor=self.predictor, data=list(hist))

        # For each true date in the tail, forecast using real history only
        for idx in range(n - days, n):
            base_date = full[idx - 1][0]
            pred_val = self.predict_tomorrow(lag_days, base_date=base_date)
            pg.data.append((full[idx][0], pred_val))

        return pg

    def check_confidence(self, days: int, lag_days: int, return_graph=False):
        """
        Compute confidence as 1 - |AUC(pred) - AUC(real)| / max(AUCs).

        Parameters:
            days         Number of tail points to compare.
            lag_days     Lag days for AR model.
            return_graph If True, also return the PredictedGraph.

        Returns:
            confidence float, and optionally the PredictedGraph.
        """
        full_pred = self.predict_days_ahead(days, lag_days)
        pred_df = pd.DataFrame(full_pred.data, columns=["Date", "Value"])
        real_df = pd.DataFrame(self.data,      columns=["Date", "Value"])

        pred_tail = pred_df.tail(days)
        real_tail = real_df.tail(days)

        area_pred = np.trapz(pred_tail["Value"])
        area_real = np.trapz(real_tail["Value"])
        diff = abs(area_pred - area_real)
        max_area = max(area_pred, area_real)
        confidence = 1 - (diff / max_area) if max_area else 0.0
        confidence = max(0.0, min(1.0, confidence))

        return (confidence, full_pred) if return_graph else confidence