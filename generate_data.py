#!/usr/bin/env python
# coding: utf-8

# In[3]:


import yfinance as yf
import pandas as pd


# In[4]:


def fetch_and_save_data(ticker: str, filename: str = "data.csv"):
    # Download 1 year of historical stock data
    df = yf.download(ticker, period="1y", interval="1d")

    if df.empty:
        print("No data found for ticker:", ticker)
        return

    # Keep only the closing price and format the date
    df = df[["Close"]].reset_index()
    df.columns = ["Date", "Value"]
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")


# In[5]:


if __name__ == "__main__":
    fetch_and_save_data("AAPL")


# In[ ]:




