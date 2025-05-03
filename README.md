# Stock Oracle

Stock Oracle is an interactive web-based dashboard for visualizing stock price trends and forecasting future stock behavior using linear regression and sentiment analysis. It provides historical price graphs, prediction tools, confidence scoring, and financial news sentiment analysis to assist with investment insights.

---
## Features 

- Visualizes historical daily stock prices with interactive graphs
-  Predicts **tomorrow’s closing value** using:
   - **Autoregressive modeling (Linear Regression)**
   - **Sentiment-based prediction from recent Yahoo Finance news**
-  Compares predicted vs actual values to compute a **confidence score**
-  Displays live news headlines with **sentiment analysis** tags
-  Easy-to-use layout with inputs for ticker, model type, and configuration

---
## Technologies Used
- **Frontend / Dashboard**
  - [Dash](https://dash.plotly.com/) by Plotly
  - Dash Bootstrap Components
- **Backend / ML Models**
  - `yfinance` (for stock data)
  - `scikit-learn` (Linear Regression)
  - `TextBlob` (sentiment analysis)
- **NLP / News Parsing**
  - Yahoo Finance Search API
  - `requests` for headline fetching

---

## How It Works

1. **Enter a Ticker Symbol (e.g. AAPL)**
2. Click **Load Data** to fetch 1 year of daily historical prices
3. The app auto-generates:
   - A historical graph
   - Latest 5 news headlines + their sentiment
4. Choose analysis type:
   - `Default`: Autoregressive ML model
   - `Sentimental`: Uses sentiment from news to predict
5. Input parameters for simulation:
   - Days Behind Today (point of divergence)
   - Lag Days (used for regression)
6. Hit **Check Confidence** to view predicted vs real chart and confidence %

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/StockOracle.git
cd StockOracle

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run the app
python main.py

The dashboard will be live at http://127.0.0.1:8050/

```
---

## Testing
Unit tests are provided in the `/tests` directory and cover:
- CSV file creation and parsing
- Prediction correctness
- Confidence bounds
- News retrieval and format

Run the tests with:
```bash
  pytest -q
```
---

## Authors
- Phineas Howell
- Praneeth Sai Ummadisetty
- Arjun Suresh
