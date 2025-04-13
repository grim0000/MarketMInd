import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from textblob import TextBlob

def process_data(hist):
    try:
        if hist is not None and not hist.empty:
            hist['Prev_Close'] = hist['Close'].shift(1)
            hist.dropna(inplace=True)

            X = hist['Prev_Close'].values.reshape(-1, 1)
            y = (hist['Close'].shift(-1) > hist['Close']).astype(int).dropna().values

            model = LinearRegression()
            model.fit(X, y)

            last_close = hist['Close'].iloc[-1]
            prediction = model.predict(np.array([[last_close]]))
            direction = "📈 Bullish" if prediction[0] > 0.5 else "📉 Bearish"
            return direction, hist.tail(10)
        else:
            return None, None
    except Exception as e:
        raise Exception(f"Error processing data: {e}")

def perform_sentiment_analysis(symbol):
    news_headlines = [
        f"{symbol} sees an upward trend amidst market optimism.",
        f"Concerns grow about {symbol}'s recent performance.",
        f"Investors stay bullish on {symbol}."
    ]

    sentiments = []
    for headline in news_headlines:
        analysis = TextBlob(headline)
        sentiments.append(analysis.sentiment.polarity)

    avg_sentiment = sum(sentiments) / len(sentiments)
    sentiment_category = "😊 Positive" if avg_sentiment > 0 else "😟 Negative" if avg_sentiment < 0 else "😐 Neutral"

    return sentiment_category, news_headlines
