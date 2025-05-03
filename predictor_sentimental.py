# Stock Oracle Group
# 5/5/2025
# File for the predictor that uses sentiment analysis of news articles
import os
import pandas as pd
from fetch_stock_news import get_yahoo_finance_news

class PredictorSentimental:
    """
        A predictor that estimates future stock prices based on the sentiment of recent news headlines.
        Uses a simple sentiment-to-percentage adjustment method based on TextBlob sentiment scores.
    """
    def __init__(self, ticker: str):
        """
            Initializes the predictor with a given stock ticker.

            Parameters:
                ticker (str): Stock ticker symbol (e.g., 'AAPL').
        """
        self.ticker = ticker

    def predict_tomorrow(self, lag_days: int = None, last_value: float = None) -> float:
        """
            Predicts tomorrow's stock price based on news sentiment.

            Parameters:
                lag_days (int, optional): Not used in this model, included for compatibility.
                last_value (float, optional): Most recent known price to base prediction on.
                                                  If not provided, falls back to last row in 'data.csv'.

            Returns:
                float: Predicted stock price for tomorrow.
        """

        # Retrieve recent news articles
        news = get_yahoo_finance_news(self.ticker)
        if not news:
            return 0.0 # No prediction if news isn't available

        # Map sentiment labels to numerical scores
        sentiment_mapping = {"Positive": 1, "Neutral": 0, "Negative": -1}
        total, count = 0, 0
        for article in news:
            score = sentiment_mapping.get(article.get("sentiment", "Neutral"), 0)
            total += score
            count += 1
        avg_sentiment = total / count if count > 0 else 0.0

        # Determine base price: use the last_value passed in if available, otherwise read the last CSV row as before
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


