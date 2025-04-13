import streamlit as st
import plotly.graph_objs as go
from fundamental import perform_fundamental_analysis
from sentiment import perform_sentiment_analysis
from indicators import add_indicators
from historical import get_historical_data
import hashlib
import time

# Set page configuration
st.set_page_config(
    page_title="Market Mind: Indian Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1E1E2E;
        color: #D4D4D8;
    }
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #60A5FA;
        margin-bottom: 1rem;
    }
    h2 {
        color: #93C5FD;
    }
    .css-1lcbmhc {
        background-color: #252537;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: #F3F4F6;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    .stTextInput input {
        background-color: #2D2D44;
        color: #D4D4D8;
        border: 1px solid #4B5EAA;
    }
    .stCheckbox label, .stRadio label {
        color: #D4D4D8;
    }
    .js-plotly-plot {
        background-color: #181825;
        border-radius: 8px;
        padding: 1rem;
        min-height: 400px; /* Ensure minimum height */
    }
    .stDataFrame {
        background-color: #2D2D44;
        color: #D4D4D8;
    }
    .stAlert {
        background-color: #7F1D1D;
        color: #FEE2E2;
        border-radius: 8px;
    }
    .section-divider {
        border-bottom: 1px solid #374151;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Centered title
st.markdown("<h1 class='title'>Market Mind: Indian Stock Analyzer 📈</h1>", unsafe_allow_html=True)

# Sidebar for preferences
with st.sidebar:
    st.markdown("### Analysis Options")
    exchange = st.radio("Select Exchange", ["NSE", "BSE"], help="Choose the stock exchange.")
    symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., RELIANCE, TCS")
    time_frame = st.selectbox("Select Time Frame", ["1mo", "6mo", "1y", "5y", "max"], help="Select data duration.")
    indicators = st.multiselect("Select Indicators", ["Moving Average (MA)", "Relative Strength Index (RSI)", "Bollinger Bands", "MACD"], default=["Moving Average (MA)"], help="Choose technical indicators.")
    show_chart = st.checkbox("Show Price Chart", value=True)
    show_volume = st.checkbox("Show Volume Chart")
    show_sentiment = st.checkbox("Show Sentiment Analysis", value=True)
    show_fundamental = st.checkbox("Show Fundamental Analysis")
    show_historical_data = st.checkbox("Show Historical Data")
    show_prediction = st.checkbox("Show Prediction Results")
    update_chart_button = st.button("Update Chart", key="update_chart")
    st.markdown("---")
    st.markdown(f"**Selected:** {symbol} on {exchange} ({time_frame})")

# Initialize session state
if 'fig' not in st.session_state:
    st.session_state['fig'] = None
if 'chart_key' not in st.session_state:
    st.session_state['chart_key'] = None
if 'sentiment_data' not in st.session_state:
    st.session_state['sentiment_data'] = {"symbol": "", "sentiment": "", "headlines": []}
if 'error' not in st.session_state:
    st.session_state['error'] = None
if 'warning' not in st.session_state:
    st.session_state['warning'] = None

# Fetch and analyze stock data
if symbol:
    if exchange.lower() not in ["nse", "bse"]:
        st.error("Please select either 'NSE' or 'BSE'.", icon="🚫")
    else:
        with st.spinner(f"Analyzing {symbol} on {exchange}..."):
            start_time = time.time()
            hist = get_historical_data(symbol, time_frame, exchange)
            if 'error' in st.session_state and st.session_state['error']:
                st.error(st.session_state['error'], icon="⚠️")
            elif hist.empty:
                st.warning(f"No data available for '{symbol}' on {exchange}. Please check the symbol or try again.", icon="⚠️")
            else:
                hist = add_indicators(hist, indicators)

                # Function to generate unique chart key
                def generate_chart_key():
                    key_source = f"{exchange}_{symbol}_{time_frame}_{'_'.join(indicators)}"
                    return hashlib.md5(key_source.encode()).hexdigest()

                # Function to update price chart
                def update_chart():
                    if hist.empty or 'Close' not in hist.columns:
                        st.error("No valid price data to render chart.", icon="⚠️")
                        return go.Figure()
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Candlestick',
                        increasing_line_color='#22C55E',
                        decreasing_line_color='#EF4444'
                    )])
                    if "Moving Average (MA)" in indicators and 'MA' in hist.columns:
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA'], mode='lines', name='MA', line=dict(color='#10B981')))
                    if "Relative Strength Index (RSI)" in indicators and 'RSI' in hist.columns:
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], mode='lines', name='RSI', line=dict(color='#F59E0B'), yaxis="y2"))
                    if "Bollinger Bands" in indicators and all(x in hist.columns for x in ['BB_Upper', 'BB_Lower']):
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='#3B82F6', dash='dash')))
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='#3B82F6', dash='dash')))
                    if "MACD" in indicators and 'MACD' in hist.columns:
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['MACD'], mode='lines', name='MACD', line=dict(color='#EC4899'), yaxis="y3"))
                    
                    fig.update_layout(
                        title=f"{symbol} Price Chart",
                        xaxis_title="Date",
                        yaxis_title="Price (INR)",
                        template="plotly_dark",
                        xaxis_rangeslider_visible=True,
                        yaxis=dict(gridcolor='#374151'),
                        plot_bgcolor='#181825',
                        paper_bgcolor='#181825',
                        font=dict(color='#D4D4D8'),
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        yaxis2=dict(title="RSI", overlaying="y", side="right", showgrid=False, range=[0, 100]),
                        yaxis3=dict(title="MACD", overlaying="y", side="right", showgrid=False, anchor="free", position=0.95)
                    )
                    return fig

                # Function to plot volume chart
                def plot_volume_chart():
                    if hist.empty or 'Volume' not in hist.columns:
                        st.error("No valid volume data to render chart.", icon="⚠️")
                        return go.Figure()
                    fig = go.Figure(data=[go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name='Volume',
                        marker_color='#3B82F6'
                    )])
                    fig.update_layout(
                        title=f"{symbol} Trading Volume",
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        template="plotly_dark",
                        plot_bgcolor='#181825',
                        paper_bgcolor='#181825',
                        font=dict(color='#D4D4D8'),
                        yaxis=dict(gridcolor='#374151')
                    )
                    return fig

                # Determine buy/sell signals
                def determine_signals(hist):
                    buy_signals = []
                    sell_signals = []
                    accuracy_count = 0
                    if len(hist) < 50 or 'Close' not in hist.columns:
                        return buy_signals, sell_signals, 0.0
                    hist['SMA50'] = hist['Close'].rolling(window=50, min_periods=1).mean()
                    hist['SMA200'] = hist['Close'].rolling(window=200, min_periods=1).mean()
                    for i in range(1, len(hist)):
                        if hist['SMA50'].iloc[i-1] < hist['SMA200'].iloc[i-1] and hist['SMA50'].iloc[i] > hist['SMA200'].iloc[i]:
                            buy_signals.append(hist.index[i])
                        elif hist['SMA50'].iloc[i-1] > hist['SMA200'].iloc[i-1] and hist['SMA50'].iloc[i] < hist['SMA200'].iloc[i]:
                            sell_signals.append(hist.index[i])
                        if (i > 1 and (hist['Close'].iloc[i] > hist['Close'].iloc[i-1]) and hist.index[i-1] in buy_signals) or \
                           (i > 1 and (hist['Close'].iloc[i] < hist['Close'].iloc[i-1]) and hist.index[i-1] in sell_signals):
                            accuracy_count += 1
                    accuracy_percentage = accuracy_count / (len(buy_signals) + len(sell_signals)) * 100 if (len(buy_signals) + len(sell_signals)) > 0 else 0.0
                    return buy_signals, sell_signals, accuracy_percentage

                # Layout with columns
                col1, col2 = st.columns([2, 1])

                with col1:
                    if show_chart:
                        st.markdown("### Price Chart")
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                        if update_chart_button or st.session_state['fig'] is None:
                            st.session_state['chart_key'] = generate_chart_key()
                            st.session_state['fig'] = update_chart()
                        if st.session_state['fig']:
                            st.plotly_chart(st.session_state['fig'], use_container_width=True, key=st.session_state['chart_key'])
                        else:
                            st.error("Failed to render price chart. Check data or indicators.", icon="⚠️")
                        if 'warning' in st.session_state and st.session_state['warning']:
                            st.warning(st.session_state['warning'], icon="⚠️")

                    if show_volume:
                        st.markdown("### Trading Volume")
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                        volume_fig = plot_volume_chart()
                        if volume_fig:
                            st.plotly_chart(volume_fig, use_container_width=True)
                        else:
                            st.error("Failed to render volume chart. Check data.", icon="⚠️")

                with col2:
                    if show_prediction:
                        st.markdown("### Trading Signals")
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                        buy_signals, sell_signals, accuracy_percentage = determine_signals(hist)
                        if buy_signals or sell_signals:
                            for buy_signal in buy_signals:
                                st.markdown(f"**📈 Buy** at {buy_signal.strftime('%Y-%m-%d')} (Accuracy: {accuracy_percentage:.2f}%)")
                            for sell_signal in sell_signals:
                                st.markdown(f"**📉 Sell** at {sell_signal.strftime('%Y-%m-%d')} (Accuracy: {accuracy_percentage:.2f}%)")
                        else:
                            st.info("No trading signals generated.", icon="ℹ️")

                    if show_sentiment:
                        with st.spinner("Analyzing sentiment..."):
                            st.markdown("### Sentiment Analysis")
                            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                            if st.session_state['sentiment_data']['symbol'] != symbol:
                                st.session_state['sentiment_data'] = perform_sentiment_analysis(symbol)
                            sentiment_data = st.session_state['sentiment_data']
                            st.markdown(f"**Sentiment:** {sentiment_data['sentiment']}")
                            for headline in sentiment_data['headlines']:
                                st.markdown(f"- {headline}")

                    if show_fundamental:
                        with st.spinner("Analyzing fundamentals..."):
                            st.markdown("### Fundamental Analysis")
                            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                            fundamental_analysis = perform_fundamental_analysis(symbol)
                            st.markdown(fundamental_analysis)

                if show_historical_data:
                    st.markdown("### Historical Data")
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.dataframe(hist, use_container_width=True)

            if 'warning' in st.session_state and st.session_state['warning'] and not show_chart:
                st.warning(st.session_state['warning'], icon="⚠️")

else:
    st.info("Enter a stock symbol to begin analysis.", icon="ℹ️")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Market Mind 2024** | Created by Dev.off()")