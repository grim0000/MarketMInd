import pandas as pd

def add_indicators(hist, selected_indicators):
    if "Moving Average (MA)" in selected_indicators:
        hist['MA'] = hist['Close'].rolling(window=20).mean()
    if "Relative Strength Index (RSI)" in selected_indicators:
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
    if "Bollinger Bands" in selected_indicators:
        hist['BB_Upper'] = hist['Close'].rolling(window=20).mean() + (2 * hist['Close'].rolling(window=20).std())
        hist['BB_Lower'] = hist['Close'].rolling(window=20).mean() - (2 * hist['Close'].rolling(window=20).std())
    if "MACD" in selected_indicators:
        hist['MACD'] = hist['Close'].ewm(span=12, adjust=False).mean() - hist['Close'].ewm(span=26, adjust=False).mean()
    return hist
