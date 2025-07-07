import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(page_title="📊 EMA Trend Analyzer", layout="wide")
st.title("📈 EMA Trend Analyzer Dashboard")

stock_symbol = st.text_input("Enter Stock Ticker (e.g. APOLLOMICRO.NS or AAPL):", value="APOLLOMICRO.NS").strip().upper()

if stock_symbol:
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=365)

    try:
        data = yf.download(stock_symbol, start=start, end=end, auto_adjust=True)

        if data.empty:
            st.error("❌ No data found. Please check the ticker.")
        else:
            data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
            data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
            data['EMA100'] = data['Close'].ewm(span=100, adjust=False).mean()
            data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

            latest = data.iloc[-1]
            close_price = latest['Close']
            ema_vals = [latest[f'EMA{p}'] for p in [20, 50, 100, 200]]

            st.subheader(f"💰 Latest Price: ₹{round(close_price, 2)}")

            trend_data = [
                (f"{p}-day EMA", round(e), "🔼 Above" if close_price > e else "🔽 Below")
                for p, e in zip([20, 50, 100, 200], ema_vals)
            ]
            df_trend = pd.DataFrame(trend_data, columns=["EMA", "Value", "Status"])
            st.table(df_trend)

            st.success("🟢 Long-term Trend: **Bullish** (Price above 200 EMA)" if close_price > ema_vals[-1]
                       else st.error("🔴 Long-term Trend: **Bearish** (Price below 200 EMA)"))

            crossover_text = ("✅ Short-Term Bullish: EMA20 > EMA50"
                              if ema_vals[0] > ema_vals[1]
                              else "⚠️ Short-Term Bearish: EMA20 < EMA50")
            st.info(crossover_text)

            st.subheader("📉 Price Chart with EMAs")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(data['Close'], label='Close', color='black')
            for p, e in zip([20, 50, 100, 200], [data['EMA20'], data['EMA50'], data['EMA100'], data['EMA200']]):
                ax.plot(e, label=f'EMA{p}', linestyle='--')
            ax.legend(); ax.grid(True)
            ax.set_title(f"{stock_symbol} – Price + EMA Trend")
            ax.set_ylabel("Price (INR)")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"⚠️ Error fetching data: {e}")
