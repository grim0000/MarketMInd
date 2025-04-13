import yfinance as yf
import pandas as pd
from datetime import datetime
import time

def test_yfinance_ticker(symbol, period="1mo", max_retries=3, retry_delay=2):
    """
    Test the yfinance library by fetching historical data for a given ticker.
    
    Args:
        symbol (str): Stock ticker (e.g., "TCS.NS" for NSE, "TCS.BO" for BSE).
        period (str): Time period for data (e.g., "1mo", "6mo", "1y", "5y", "max").
        max_retries (int): Maximum number of retry attempts.
        retry_delay (int): Delay between retries in seconds.
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch data for {symbol} with period {period}...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                print(f"No data available for {symbol}. The ticker might be invalid or delisted.")
                return None

            print(f"Successfully fetched data for {symbol} as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\nFirst 5 rows of data:")
            print(hist.head())
            print("\nLast 5 rows of data:")
            print(hist.tail())
            print(f"Total rows: {len(hist)}")
            return hist

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to get ticker '{symbol}' after {max_retries} attempts.")
                return None

def main():
    # List of test tickers (Indian stocks on NSE and BSE)
    test_tickers = [
        "TCS.NS",    # Tata Consultancy Services (NSE)
        "RELIANCE.NS",  # Reliance Industries (NSE)
        "INFY.NS",    # Infosys (NSE)
        "TCS.BO",    # Tata Consultancy Services (BSE)
        "RELIANCE.BO"  # Reliance Industries (BSE)
    ]
    
    test_periods = ["1mo", "6mo", "1y"]  # Test different periods

    for ticker in test_tickers:
        print(f"\nTesting {ticker}:")
        for period in test_periods:
            data = test_yfinance_ticker(ticker, period)
            if data is not None:
                # Optionally save to CSV for inspection
                data.to_csv(f"{ticker}_{period}.csv")
            print("-" * 50)

if __name__ == "__main__":
    main()