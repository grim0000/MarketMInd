import yfinance as yf

def get_historical_data(symbol, time_frame="1y"):
    """
    Fetch historical stock data for a given symbol and time frame.

    Parameters:
    - symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    - time_frame (str): The time frame for historical data (e.g., '1d', '5d', '1mo', '6mo', '1y', '5y', 'max').

    Returns:
    - pandas.DataFrame: A DataFrame containing the historical data.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=time_frame)
        return hist
    except Exception as e:
        return f"Error fetching historical data: {e}"
