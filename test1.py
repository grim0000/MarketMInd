import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from textblob import TextBlob
import numpy as np
from huggingface_hub import InferenceClient

# Hugging Face API setup
api_key = "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"
client = InferenceClient(api_key=api_key)

# Streamlit app setup with custom theme
st.set_page_config(
    page_title="Market Mind",
    page_icon="📈",
    layout="wide",
)

# App title and subheading
st.markdown(
    """
    <style>
    .main-title {
        font-size: 40px;
        font-weight: bold;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 20px;
        color: gray;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="main-title">MARKET MIND</div>
    <div class="sub-title">Indian Stock Analyzer</div>
    """,
    unsafe_allow_html=True,
)

# Sidebar for user preferences
st.sidebar.title("⚙️ Preferences")
symbol = st.sidebar.text_input("Enter the stock symbol (e.g., RELIANCE, TCS):")
time_frame = st.sidebar.selectbox(
    "Select Time Frame",
    ["1d", "5d", "1mo", "6mo", "1y", "5y", "max"]
)
indicators = st.sidebar.multiselect(
    "Select Indicators",
    ["Moving Average (MA)", "Relative Strength Index (RSI)", "Bollinger Bands", "MACD"]
)

# Function to fetch stock data
def fetch_stock_data(ticker, period):
    try:
        ticker_data = yf.Ticker(ticker)
        hist = ticker_data.history(period=period)
        return hist
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to add selected indicators to the data
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

# Function for fundamental analysis using Hugging Face API
def perform_fundamental_analysis(symbol):
    prompt = f"Provide a detailed fundamental analysis for the stock symbol '{symbol}'."
    messages = [{"role": "user", "content": prompt}]
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=messages,
            max_tokens=500
        )
        return completion.choices[0].message['content']
    except Exception as e:
        st.error(f"Error generating fundamental analysis: {e}")
        return "Could not fetch fundamental analysis."

# Main content
if symbol:
    st.markdown(f"### 📊 Analyzing Stock: **{symbol.upper()}**")

    try:
        with st.spinner("Fetching data and running analysis..."):
            hist = fetch_stock_data(symbol, period=time_frame)

            if hist is None or hist.empty:
                st.error("No data found for the given symbol. Please check the symbol name.")
            else:
                # Add selected indicators
                hist = add_indicators(hist, indicators)

                st.markdown("#### ⏳ Historical Data")
                st.dataframe(hist.tail(10), height=200)

                st.markdown("#### 📈 Price Chart")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(hist.index, hist['Close'], label="Closing Price", color="#FF5733")
                if "Moving Average (MA)" in indicators:
                    ax.plot(hist.index, hist['MA'], label="Moving Average (MA)", color="#33A1FF")
                if "Bollinger Bands" in indicators:
                    ax.plot(hist.index, hist['BB_Upper'], label="Bollinger Upper Band", color="green", linestyle="--")
                    ax.plot(hist.index, hist['BB_Lower'], label="Bollinger Lower Band", color="red", linestyle="--")
                if "MACD" in indicators:
                    ax.plot(hist.index, hist['MACD'], label="MACD", color="purple")
                ax.set_title(f"{symbol.upper()} - {time_frame} Price Chart", fontsize=16)
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)

                # Fundamental Analysis
                st.markdown("#### 📊 Fundamental Analysis ")
                fundamental_analysis = perform_fundamental_analysis(symbol)
                st.write(f"**Analysis:** {fundamental_analysis}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    st.markdown("### 🔍 Please enter a stock symbol to begin.")
