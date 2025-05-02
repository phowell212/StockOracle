# Praneeth Sai Ummadisetty
# 04/08/2025
# This is function where a particular stock articles are fetched
import requests
from textblob import TextBlob
from bs4 import BeautifulSoup
import time
from textblob.en import polarity


def analyze_sentiment_for_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(url, headers = headers, timeout=10)
        print("status code: ", response.status_code)
        if response.status_code == 429:
            print("Reached limit. Retrying after 0.5 secs.")
            time.sleep(0.5)
            response = requests.get(url, headers = headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch content from {url}")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        if len(content) < 200:
            print(f"Not enough content from {url}")
            return None
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity
        return polarity

    except Exception as e:
        print(f"Error analyzing sentiment for {url}: {e}")
        return None

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
        total_polarity = 0
        overall_trend = "Unknown"
        count = 0
        for item in data.get("news", [])[:5]:
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            # sentiment = TextBlob(title).sentiment.polarity
            # sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
            polarity = analyze_sentiment_for_content(link)
            if polarity is not None:
                count += 1
                total_polarity += polarity
                sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            else:
                # blob = TextBlob(title)
                # polarity = blob.sentiment.polarity
                # sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
                sentiment_label = "Unknown"
            news_items.append({"title": title, "url": link, "sentiment": sentiment_label})
            #Overall sentiment
            if count > 0:
                avg_polarity = total_polarity / count
                overall_trend = "Upward" if avg_polarity > 0 else "Downward" if avg_polarity < 0 else "Neutral"
                print(f"Overall sentiment trend for '{stock_symbol}': {overall_trend} (Average polarity: {avg_polarity:.2f}")
            else:
                print("Unable to determine overall sentiment due to insufficient data.")
        return {"articles" : news_items, "overall_sentiment" : overall_trend}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return {"articles" : [], "overall_sentiment" : "Unknown"}
