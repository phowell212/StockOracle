# tests/test_fetch.py
from fetch_stock_data import fetch_and_save_data
import os, pandas as pd

"""
Verifies that 'fetch_and_save_data()' retrieves one year of price data from Yahoo Finance and writes a non-empty CSV with 
the expected two columns ('Date','Value'). Ensures basic data-ingestion pipeline is working and that external I/O succeeds
(API -> disk).
"""
def test_fetch_creates_csv(tmp_path):
    """yfinance fetch writes non‑empty CSV."""
    file = tmp_path / "sample.csv"
    fetch_and_save_data("AAPL", str(file))
    assert file.exists()
    df = pd.read_csv(file)
    assert not df.empty
    assert {"Date", "Value"} <= set(df.columns)
