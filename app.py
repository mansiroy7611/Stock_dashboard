# interactive_stock_dashboard.py

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pytz

# Page settings
st.set_page_config(page_title="📈 Interactive Stock Dashboard", layout="wide")
st.title("📊 MarketPulse: Interactive Stock Dashboard")


# --- Sidebar: Search and Settings ---
st.sidebar.header("🔍 Search & Settings")

# US + India Stocks
stock_options = {
    # US Stocks
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Tesla (TSLA)": "TSLA",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "Meta (META)": "META",
    "NVIDIA (NVDA)": "NVDA",
    "Netflix (NFLX)": "NFLX",
    "Intel (INTC)": "INTC",
    "AMD (AMD)": "AMD",
    # Indian Stocks (NSE)
    "Wipro (WIPRO.NS)": "WIPRO.NS",
    "Infosys (INFY.NS)": "INFY.NS",
    "TCS (TCS.NS)": "TCS.NS",
    "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS",
    "Reliance (RELIANCE.NS)": "RELIANCE.NS"
}

selected_stock = st.sidebar.selectbox("Choose Company", list(stock_options.keys()))
symbol = stock_options[selected_stock]

interval = st.sidebar.radio("Select Interval", ["Daily", "Weekly", "Monthly"])

# --- Fetch Yahoo Finance Data ---
def get_yahoo_stock_data(symbol, interval):
    ticker = yf.Ticker(symbol)
    if interval == "Daily":
        df = ticker.history(period="6mo", interval="1d")
    elif interval == "Weekly":
        df = ticker.history(period="1y", interval="1wk")
    else:
        df = ticker.history(period="2y", interval="1mo")
    df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
    df.index = df.index.tz_localize(None)  # Remove timezone info for comparison
    return df

# --- Tabs Layout ---
if symbol:
    df = get_yahoo_stock_data(symbol, interval)

    if df is not None and not df.empty:
        tab1, tab2, tab3 = st.tabs(["📈 Chart View", "📉 Volume & Table", "📥 Export"])

        with tab1:
            min_date, max_date = df.index.min(), df.index.max()
            start, end = st.sidebar.date_input("📆 Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
            df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

            show_sma = st.checkbox("Show SMA20 & SMA50", value=True)
            if show_sma:
                df["SMA20"] = df["Close"].rolling(window=20).mean()
                df["SMA50"] = df["Close"].rolling(window=50).mean()

            chart_type = st.radio("📊 Choose Chart Type", ["Candlestick", "Line", "Area"], horizontal=True)

            if chart_type == "Candlestick":
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candlestick"))
            if show_sma:
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20", line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA 50", line=dict(color='orange')))
                fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Line":
                st.line_chart(df["Close"])

            elif chart_type == "Area":
                st.area_chart(df["Close"])


        with tab2:
            st.subheader("📉 Volume Chart")
            st.bar_chart(df["Volume"])
            st.subheader("📋 Latest 10 Data Points")
            st.dataframe(df.tail(10))

        with tab3:
            st.subheader("📥 Download Data")
            st.download_button("⬇️ Download CSV", df.to_csv().encode("utf-8"), file_name=f"{symbol}_{interval}_data.csv", mime="text/csv")

    else:
        st.error("⚠️ Could not fetch stock data.")
else:
    st.info("🔍 Start by selecting a stock from the sidebar.")
