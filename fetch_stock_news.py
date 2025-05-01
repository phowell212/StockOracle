# Praneeth Sai Ummadisetty
# 04/08/2025
# This is function where a particular stock articles are fetched
import requests

def get_yahoo_finance_news(stock_symbol):
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
            news_items.append({"title": title, "url": link})

        return news_items

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return []
