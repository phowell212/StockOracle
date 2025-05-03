# Stock Oracle Group
# 5/5/2025
# File for the predictor that uses sentiment analysis of news articles

"""
This module defines a sentiment-based predictor that analyzes news headlines using TextBlob
to forecast stock price movements. It integrates with Yahoo Finance's unofficial API to
fetch relevant news articles and maps sentiment polarity to stock price predictions.

The predictor can estimate tomorrow’s price or simulate multiple days ahead using historical data.
"""

import os
import pandas as pd
from fetch_stock_news import get_yahoo_finance_news
from predictor_default import PredictedGraph

# Pycharm wanted me to do this
def get_historical_price(date: pd.Timestamp) -> float:
    """
        Retrieves a historical stock price from 'data.csv' for a given date.

        If the date is not found, uses the last available price before the given date,
        or falls back to the first available or default value.

        Args:
            date (pd.Timestamp): Date to retrieve the price for.

        Returns:
            float: Historical price for the date, or a fallback value.
    """
    filename = "data.csv"
    default_price = 100.0
    if not os.path.exists(filename):
        return default_price

    df = pd.read_csv(filename)
    if df.empty or "Date" not in df or "Value" not in df:
        return default_price

    df["Date"] = pd.to_datetime(df["Date"])
    # Exact match
    exact = df[df["Date"] == date]
    if not exact.empty:
        return float(exact.iloc[0]["Value"])

    # Otherwise, use last available date before target
    before = df[df["Date"] < date]
    if not before.empty:
        return float(before.iloc[-1]["Value"])

    # Otherwise fallback to first or default
    return float(df.iloc[0]["Value"]) if not df.empty else default_price


class PredictorSentimental:
    """
        A predictor that uses sentiment analysis of recent news headlines to estimate stock price movement.
    """

    def __init__(self, ticker: str):
        """
            Initializes the predictor with a stock ticker symbol.

            Args:
                ticker (str): The stock symbol to analyze (e.g., 'AAPL').
        """
        self.ticker = ticker

    def predict_tomorrow(self, lag_days: int, lag_day_number: int = None) -> float:
        """
            Predicts the next day's stock price using sentiment scores from recent news.

            If lag_day_number is provided, it performs a simulation-like prediction for a prior day.
            Otherwise, it uses current sentiment to predict tomorrow's price.

            Args:
                lag_days (int): Number of lag days used in the prediction logic.
                lag_day_number (int, optional): The nth day into the simulation (used for multi-day prediction).

            Returns:
                float: The predicted closing price.
        """
        if lag_day_number:
            # Compute target date for sentiment and base price lookup
            today = pd.Timestamp.today().normalize()
            offset = lag_days + lag_day_number
            target_date = today - pd.Timedelta(days=offset)
            target_str = target_date.strftime("%Y-%m-%d")

            # Fetch news for the target date
            articles = get_yahoo_finance_news(self.ticker, date=target_str)

            # Compute average sentiment score
            if articles:
                mapping = {"Positive": 1, "Neutral": 0, "Negative": -1}
                scores = [mapping.get(a.get("sentiment", "Neutral"), 0) for a in articles]
                avg_sentiment = sum(scores) / len(scores)
            else:
                avg_sentiment = 0.0

            # Determine the base price from historical data.csv
            base_price = get_historical_price(target_date)

            # Apply sentiment adjustment: ±25% per sentiment point
            return base_price * (1 + 0.25 * avg_sentiment)

        # If no lag day number, use the normal prediction logic
        else:
            news = get_yahoo_finance_news(self.ticker)
            if not news:
                return 0.0

            # Map sentiment labels to numerical scores
            sentiment_mapping = {"Positive": 1, "Neutral": 0, "Negative": -1}
            total, count = 0, 0
            for article in news:
                score = sentiment_mapping.get(article.get("sentiment", "Neutral"), 0)
                total += score
                count += 1
            avg_sentiment = total / count if count > 0 else 0.0

            # Determine base price: use the last_value passed in if available, otherwise read the last CSV row as before
            if os.path.exists("data.csv"):
                try:
                    df = pd.read_csv("data.csv")
                    base = df.iloc[-1]["Value"]
                except Exception:
                    base = 100.0

            # Adjust prediction: 25% change per sentiment point
            prediction = base * (1 + 0.25 * avg_sentiment)
            return prediction

    def predict_days_ahead(self, days: int, lag_days: int) -> 'PredictedGraph':
        """
            Simulates stock predictions for a future window by applying sentiment scores iteratively.

            Args:
                days (int): Number of days to simulate ahead.
                lag_days (int): Number of lag days used in the simulation logic.

            Returns:
                PredictedGraph: A graph object containing the predicted time series.
        """
        if not os.path.exists("data.csv"):
            return PredictedGraph(predictor=self, data=[])

        df = pd.read_csv("data.csv")
        if df.empty or "Date" not in df or "Value" not in df:
            return PredictedGraph(predictor=self, data=[])

        df["Date"] = pd.to_datetime(df["Date"])
        series = df.set_index("Date")["Value"]

        # Create a new PredictedGraph with the historical slice
        initial_data = list(zip(series.index.strftime("%Y-%m-%d"), series.values))
        predictions = PredictedGraph(predictor=self, data=initial_data[: -days])

        days_since_divergence = 0

        # Generate predictions iteratively
        while True:
            last_date = predictions.data[-1][0]
            if isinstance(last_date, str):
                last_date = pd.Timestamp(last_date)

            if last_date >= series.index[-1]:
                break

            next_value = self.predict_tomorrow(lag_days, days_since_divergence)
            next_date = last_date + pd.Timedelta(days=1)
            predictions.data.append((next_date.strftime("%Y-%m-%d"), next_value))
            days_since_divergence += 1

        return predictions
