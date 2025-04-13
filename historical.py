import yfinance as yf
import pandas as pd
import requests
import time
import streamlit as st

def validate_ticker(symbol, exchange):
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    ticker = f"{symbol}{suffix}"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200 and response.json().get("chart", {}).get("result"):
            return True, ticker
        return False, ticker
    except Exception:
        return False, ticker

def get_historical_data(symbol, time_frame="1y", exchange="NSE"):
    symbol = symbol.strip().replace("$", "").upper()
    is_valid, ticker_symbol = validate_ticker(symbol, exchange)
    if not is_valid:
        st.session_state['error'] = f"Invalid ticker '{ticker_symbol}'. It may not exist on {exchange}. For example, 'AAPL' is listed on NASDAQ, not NSE."
        return pd.DataFrame()

    periods = [time_frame, "1y"] if time_frame == "1mo" else [time_frame]
    max_retries = 3
    for period in periods:
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period=period, auto_adjust=True, timeout=10)
                if hist.empty:
                    st.session_state['error'] = f"No data found for '{ticker_symbol}' on {exchange} for period '{period}'. Try a different period or check the symbol."
                    continue
                hist = hist[['Open', 'High', 'Low', 'Close', 'Volume']]
                if hist.index.duplicated().any():
                    hist = hist[~hist.index.duplicated(keep='first')]
                if len(hist) < 10:
                    st.session_state['warning'] = f"Only {len(hist)} data points fetched for '{ticker_symbol}'. Consider a longer time frame."
                st.write(f"Debug: Fetched {len(hist)} rows for {ticker_symbol} with columns: {hist.columns.tolist()}")
                if 'error' in st.session_state:
                    del st.session_state['error']
                return hist
            except Exception as e:
                if "Expecting value: line 1 column 1" in str(e):
                    st.session_state['error'] = f"Failed to fetch data for '{ticker_symbol}'. The ticker may be invalid or not listed on {exchange}."
                else:
                    st.session_state['error'] = f"Error fetching data for '{ticker_symbol}': {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        if period == periods[-1]:
            return pd.DataFrame()
    return pd.DataFrame()