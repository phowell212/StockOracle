# Stock Oracle Group
# 4/11/2025
# Script to fetch and save stock data using yfinance
import yfinance as yf


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

    # Cast to int to match the graph class format
    df["Value"] = df["Value"].round().astype(int)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")
