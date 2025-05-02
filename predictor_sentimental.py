# predictor_sentimental.py

import os
import pandas as pd
from fetch_stock_news import get_yahoo_finance_news

class PredictorSentimental:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def predict_tomorrow(self, lag_days: int = None, last_value: float = None) -> float:

        # Retrieve recent news articles
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

        # Determine base price: use the last_value passed in if available,
        # otherwise read the last CSV row as before
        if last_value is None:
            if os.path.exists("data.csv"):
                try:
                    df = pd.read_csv("data.csv")
                    base = df.iloc[-1]["Value"]
                except Exception:
                    base = 100.0
            else:
                base = 100.0
        else:
            base = last_value

        # Adjust prediction: 25% change per sentiment point
        prediction = base * (1 + 0.25 * avg_sentiment)
        return prediction
