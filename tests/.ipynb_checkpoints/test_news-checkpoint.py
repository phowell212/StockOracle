# +
from fetch_stock_news import get_yahoo_finance_news

"""
Lightweight test for the news‑scraping helper in `fetch_stock_news.py`. Simply verifies that `get_yahoo_finance_news
(<ticker>)` returns a Python list, indicating the HTTP request, parsing, and basic error handling succeeded.
"""

def test_news_returns_list():
    news = get_yahoo_finance_news("AAPL")
    assert isinstance(news, list)
