# Stock Oracle Group
# 5/5/2025
# File for the predictor that uses sentiment analysis of news articles
import os
import pandas as pd
from fetch_stock_news import get_yahoo_finance_news
from predictor_default import PredictedGraph

class PredictorSentimental:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def predict_tomorrow(self, lag_days: int, lag_day_number: int = None) -> float:
        if lag_day_number:
            # 1) Compute target date for sentiment and base price lookup
            today = pd.Timestamp.today().normalize()
            offset = lag_days + lag_day_number
            target_date = today - pd.Timedelta(days=offset)
            target_str = target_date.strftime("%Y-%m-%d")

            # 2) Fetch news for the target date
            articles = get_yahoo_finance_news(self.ticker, date=target_str)

            # 3) Compute average sentiment score
            if articles:
                mapping = {"Positive": 1, "Neutral": 0, "Negative": -1}
                scores = [mapping.get(a.get("sentiment", "Neutral"), 0) for a in articles]
                avg_sentiment = sum(scores) / len(scores)
            else:
                avg_sentiment = 0.0

            # 4) Determine the base price from historical data.csv
            base_price = self.get_historical_price(target_date)

            # 5) Apply sentiment adjustment: ±25% per sentiment point
            return base_price * (1 + 0.25 * avg_sentiment)

        # if no lag day number, use the normal prediction logic
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

    def get_historical_price(self, date: pd.Timestamp) -> float:
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

