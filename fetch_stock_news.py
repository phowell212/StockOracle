# Praneeth Sai Ummadisetty
# 04/08/2025
# This is function where a particular stock articles are fetched
import requests
from textblob import TextBlob
from textblob.en import sentiment

def get_yahoo_finance_news(stock_symbol):
    """
        Fetches the 5 most recent news articles related to the given stock symbol
        from Yahoo Finance and performs sentiment analysis on the headlines.

        Parameters:
            stock_symbol (str): The ticker symbol of the stock (e.g., "AAPL").

        Returns:
            list[dict]: A list of dictionaries, each containing:
                - title (str): The headline of the news article.
                - url (str): The link to the full article.
                - sentiment (str): Sentiment label ("Positive", "Negative", or "Neutral").
        """
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={stock_symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        news_items = []
        for item in data.get("news", [])[:5]:
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            sentiment = TextBlob(title).sentiment.polarity
            sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
            news_items.append({"title": title, "url": link, "sentiment": sentiment_label})

        return news_items

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return []
