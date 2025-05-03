# Stock Oracle Group
# 5/2/2025
# File for the predictor that fetches news articles from Yahoo Finance and performs sentiment analysis
import requests
from textblob import TextBlob
import datetime

def get_yahoo_finance_news(stock_symbol: str, date: str = None):
    """
        Fetches news articles related to a given stock symbol from Yahoo Finance and analyzes their sentiment.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., 'AAPL').
            date (str, optional): A date string in 'YYYY-MM-DD' format. If provided, only news from this date is returned.

        Returns:
            list[dict]: A list of dictionaries where each dictionary represents a news article with:
                - 'title': The article title.
                - 'url': The link to the article.
                - 'sentiment': A label indicating the sentiment ('Positive', 'Neutral', or 'Negative').
                - 'date': The article's publication date in 'YYYY-MM-DD' format.

        Notes:
            - Limits to 5 most recent articles if no date filter is provided.
            - Uses TextBlob for sentiment analysis based on the article title.
    """
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={stock_symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("news", [])
        # Limit to top 5 if no date filter
        if date is None:
            items = items[:5]

        news_list = []
        for item in items:
            ts = item.get("providerPublishTime")
            if ts is None:
                continue
            pub_date = datetime.datetime.fromtimestamp(ts).date()

            # If a date filter is provided, skip non-matching
            if date is not None:
                try:
                    desired = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    # Bad format: ignore filter
                    desired = None
                if desired and pub_date != desired:
                    continue

            title = item.get("title", "No title")
            link = item.get("link", "No link")
            polarity = TextBlob(title).sentiment.polarity
            sentiment_label = (
                "Positive" if polarity > 0 else
                "Negative" if polarity < 0 else
                "Neutral"
            )

            news_list.append({
                "title": title,
                "url": link,
                "sentiment": sentiment_label,
                "date": pub_date.isoformat()
            })

        return news_list

    except requests.RequestException as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return []
