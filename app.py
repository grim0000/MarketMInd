import streamlit as st
import plotly.graph_objs as go
from fundamental import perform_fundamental_analysis
from sentiment import perform_sentiment_analysis
from indicators import add_indicators
from historical import get_historical_data
import hashlib
import importlib


# Set the page configuration to increase width to full screen
st.set_page_config(
    page_title="Market Mind: Indian Stock Analyzer",
    page_icon="📈",
    layout="wide"  # This layout setting increases the width of the content area
)

# Inject custom CSS to ensure full-width display
st.markdown(
    """
    <style>
    .reportview-container {
        max-width: none;  /* Removes the default maximum width restriction */
        width: 100vw;     /* Set the width to the full viewport width */
    }

    .title {
        text-align: center; /* Centers the title */
        font-size: 3rem;     /* Increases the font size for emphasis */
        font-weight: bold;   /* Makes the font bold for emphasis */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Centered title
st.markdown("<h1 class='title'>Market Mind: Indian Stock Analyzer 📈</h1>", unsafe_allow_html=True)

# Your existing Streamlit code here...



# Streamlit app setup
# st.title("Market Mind: Indian Stock Analyzer")

api_key = "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"

# Sidebar for preferences
exchange = st.sidebar.radio("Select Exchange", ["NSE", "BSE"])
symbol = st.sidebar.text_input("Enter the stock symbol:")
time_frame = st.sidebar.selectbox("Select Time Frame", ["1mo", "6mo", "1y", "5y", "max"])
indicators = st.sidebar.multiselect("Select Indicators", ["Moving Average (MA)", "Relative Strength Index (RSI)", "Bollinger Bands", "MACD"])
show_chart = st.sidebar.checkbox("Show Price Chart", True)
show_sentiment = st.sidebar.checkbox("Show Sentiment Analysis", True)
show_fundamental = st.sidebar.checkbox("Show Fundamental Analysis", False)
show_historical_data = st.sidebar.checkbox("Show Historical Data", False)
show_prediction = st.sidebar.checkbox("Show Prediction Results")
show_volume = st.sidebar.checkbox("Show Volume Chart")
update_chart_button = st.button("Update Chart")


# Initialize session state variables if not already present
if 'fig' not in st.session_state:
    st.session_state['fig'] = None
if 'chart_key' not in st.session_state:
    st.session_state['chart_key'] = None
if 'show_prediction' not in st.session_state:
    st.session_state['show_prediction'] = show_prediction

# Fetch and analyze stock data
if symbol:
    if exchange.lower() not in ["nse", "bse"]:
        st.error("Invalid exchange. Please select either 'NSE' or 'BSE'.")
    else:
        st.write(f"Analyzing {exchange} {symbol}...")
        hist = get_historical_data(symbol, time_frame)

        # Add indicators to the data
        hist = add_indicators(hist, indicators)

        # Function to generate a unique key for the plotly chart
        def generate_chart_key():
            key_source = f"{exchange}_{symbol}_{time_frame}_{'_'.join(indicators)}"
            return hashlib.md5(key_source.encode()).hexdigest()

        # Function to update the price chart with the latest data
        def update_chart():
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Candlestick'
            )])

            # Add other indicators if selected
            if "Moving Average (MA)" in indicators:
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA'], mode='lines', name='MA', line=dict(color='green')))
            if "Bollinger Bands" in indicators:
                fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='green', dash='dash')))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='red', dash='dash')))

            # Plot buy/sell signals as markers on the chart
            buy_signals, sell_signals, accuracy_percentage = determine_signals(hist)
            for buy_signal in buy_signals:
                fig.add_trace(go.Scatter(x=[buy_signal], y=[hist.loc[buy_signal, 'Close']], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='Buy Signal'))
            for sell_signal in sell_signals:
                fig.add_trace(go.Scatter(x=[sell_signal], y=[hist.loc[sell_signal, 'Close']], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Sell Signal'))

            fig.update_layout(title=f"{symbol} Price Chart", xaxis_title="Date", yaxis_title="Price", template="plotly_dark", xaxis_rangeslider_visible=False)
            return fig

        # Function to plot the volume chart
        def plot_volume_chart(hist):
            fig = go.Figure(data=[go.Scatter(
                x=hist.index,
                y=hist['Volume'],
                mode='lines',
                name='Volume',
                line=dict(color='blue')
            )])
            fig.update_layout(title=f"{symbol} Trading Volume", xaxis_title="Date", yaxis_title="Volume", template="plotly_dark")
            return fig
        

        # Determine buy/sell signals based on moving average crossover strategy
        def determine_signals(hist):
            buy_signals = []
            sell_signals = []
            accuracy_count = 0

            # Check for sufficient data to compute SMAs
            if len(hist) < 200:  # Minimum length for SMA calculation
                return buy_signals, sell_signals, 0.0

            hist['SMA50'] = hist['Close'].rolling(window=50, min_periods=1).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200, min_periods=1).mean()

            for i in range(1, len(hist)):
                if hist['SMA50'][i-1] < hist['SMA200'][i-1] and hist['SMA50'][i] > hist['SMA200'][i]:
                    buy_signals.append(hist.index[i])
                elif hist['SMA50'][i-1] > hist['SMA200'][i-1] and hist['SMA50'][i] < hist['SMA200'][i]:
                    sell_signals.append(hist.index[i])
                # Calculate accuracy based on actual buy/sell results
                if (i > 1 and (hist['Close'][i] > hist['Close'][i-1]) and (i-1) in buy_signals) or \
                (i > 1 and (hist['Close'][i] < hist['Close'][i-1]) and (i-1) in sell_signals):
                    accuracy_count += 1

            accuracy_percentage = accuracy_count / (len(hist) - 1) * 100 if len(hist) > 1 else 0.0

            return buy_signals, sell_signals, accuracy_percentage

        # Display real-time chart
        st.title(symbol)
        if show_chart:
            st.subheader("Price Chart with Selected Indicators")

            # Check if there's an existing chart in session state
            if 'fig' not in st.session_state or 'chart_key' not in st.session_state or st.session_state['fig'] is None:
                st.session_state['chart_key'] = generate_chart_key()
                st.session_state['fig'] = update_chart()
            else:
                # Update the existing chart
                if update_chart_button:
                    hist = get_historical_data(symbol, time_frame)  # Fetch updated historical data
                    hist = add_indicators(hist, indicators)
                    st.session_state['fig'] = update_chart()

            # Display the chart
            st.plotly_chart(st.session_state['fig'], use_container_width=True, key=st.session_state['chart_key'])
            # Display volume chart if selected
        if show_volume:
            st.subheader("Trading Volume Chart")
            volume_chart = plot_volume_chart(hist)
            st.plotly_chart(volume_chart, use_container_width=True)

        # Display historical data
        if show_historical_data:
            st.subheader("Historical Data")
            st.write(hist)

        

        # Determine and display buy/sell signals
        if st.session_state['show_prediction']:
            buy_signals, sell_signals, accuracy_percentage = determine_signals(hist)
            if buy_signals or sell_signals:
                st.subheader("Trading Signals")
                for buy_signal in buy_signals:
                    st.write(f"**📈 Buy** at {buy_signal} (Accuracy: {accuracy_percentage:.2f}%)", unsafe_allow_html=True)
                for sell_signal in sell_signals:
                    st.write(f"**📉 Sell** at {sell_signal} (Accuracy: {accuracy_percentage:.2f}%)", unsafe_allow_html=True)

        # Display sentiment analysis
        if show_sentiment:
            st.subheader("Sentiment Analysis")
            # Check if 'sentiment_data' is in session state and if the symbol is the same
            if 'sentiment_data' not in st.session_state or st.session_state['sentiment_data']['symbol'] != symbol:
                st.session_state['sentiment_data'] = perform_sentiment_analysis(symbol)  # Pass symbol only
            sentiment_data = st.session_state['sentiment_data']
            st.write(f"**Sentiment: {sentiment_data['sentiment']}**")
            for headline in sentiment_data['headlines']:
                st.write(f"- {headline}")

        # Display fundamental analysis
        if show_fundamental:
            st.subheader("📝 Fundamental Analysis")
            st.sidebar.subheader("Fundamental Analysis")
            fundamental_analysis = perform_fundamental_analysis(symbol, api_key)
            st.write(f"**📝 Fundamental Analysis**\n{fundamental_analysis}")

        # Display prediction results
        if show_prediction:
            try:
                # Load the prediction module
                prediction_module = importlib.import_module('prediction')  # Import the prediction module
                direction, analysis_data = prediction_module.process_data(hist)

                if direction:
                    st.subheader("Prediction Results")
                    st.write(f"**Predicted Direction (Linear Regression):** {direction}")
                    st.write("**Recent Historical Data:**")
                    st.dataframe(analysis_data, height=200)
                else:
                    st.write("No prediction data available.")

            except Exception as e:
                st.error(f"Error loading prediction module: {e}")
       

else:
    st.write("Enter a stock symbol to start analyzing.")

# Footer for the sidebar
st.sidebar.markdown("Market Mind 2024 | Created by Dev.off()")
