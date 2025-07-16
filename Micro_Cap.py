import requests
import pandas as pd

API_KEY = "YWUEhUuKUkvl56P00pndf5dbJZwuFLtE"
BASE_URL = "https://financialmodelingprep.com/api/v3"
TICKER_LIMIT = 100
SCAN_LIMIT = 83  # 83 tickers × 3 endpoints = 249 API calls (safe)

def get_microcap_tickers():
    url = f"{BASE_URL}/stock-screener"
    params = {
        "marketCapLowerThan": 125_000_000,
        "exchange": "NASDAQ,NYSE,AMEX",
        "limit": TICKER_LIMIT,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return [stock["symbol"] for stock in response.json()]

def get_fundamentals(ticker):
    try:
        profile = requests.get(f"{BASE_URL}/profile/{ticker}?apikey={API_KEY}").json()
        ratios = requests.get(f"{BASE_URL}/ratios-ttm/{ticker}?apikey={API_KEY}").json()
        metrics = requests.get(f"{BASE_URL}/key-metrics-ttm/{ticker}?apikey={API_KEY}").json()

        if not profile or "symbol" not in profile[0]:
            return None

        p = profile[0]
        r = ratios[0] if ratios else {}
        m = metrics[0] if metrics else {}

        cash = p.get("cash", 0)
        if cash is None or isinstance(cash, str):
            return None
        if cash >= 5_000_000:
            return None

        high_low = p.get("range", "N/A-N/A").split("-")
        low_52w = high_low[0].strip()
        high_52w = high_low[1].strip() if len(high_low) > 1 else "N/A"

        return {
            "Ticker": p.get("symbol"),
            "Company Name": p.get("companyName", "N/A"),
            "Stock Price": p.get("price", "N/A"),
            "Market Cap": p.get("mktCap", "N/A"),
            "Cash & Equivalents": cash,
            "Total Debt": p.get("debt", "N/A"),
            "Free Cash Flow": m.get("freeCashFlowTTM", "N/A"),
            "Revenue TTM": m.get("revenueTTM", "N/A"),
            "Revenue Growth %": r.get("revenueGrowthTTM", "N/A"),
            "Debt/Equity Ratio": r.get("debtEquityTTM", "N/A"),
            "Current Ratio": r.get("currentRatioTTM", "N/A"),
            "52W High": high_52w,
            "52W Low": low_52w,
            "Short Interest": p.get("shortInterest", "N/A")
        }

    except Exception:
        return None

def run_screener():
    tickers = get_microcap_tickers()
    results = []

    for i, ticker in enumerate(tickers[:SCAN_LIMIT]):
        data = get_fundamentals(ticker)
        if data:
            results.append(data)

    df = pd.DataFrame(results)
    df.to_excel("microcap_cash_under5m.xlsx", index=False)

if __name__ == "__main__":
    run_screener()
