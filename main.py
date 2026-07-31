import os
import time
from threading import Thread
from flask import Flask
import pandas as pd
import requests
import ta
import yfinance as yf

app = Flask(__name__)

TELEGRAM_TOKEN = "8728680154:AAHMZw_KD4XWHTMoTAozEqd3nmkPKiMDBYk"
CHAT_ID = "8596188242"

WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "SBIN.NS",
    "AXISBANK.NS",
]


def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(
            url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        )
    except Exception as e:
        print(f"Error sending telegram alert: {e}")


def run_analytics_loop():
    while True:
        print("🔍 Scanning Market...")
        for symbol in WATCHLIST:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="2mo", interval="1d")
                if len(df) < 20:
                    continue

                df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
                df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
                latest = df.iloc[-1]

                if latest["Close"] > latest["EMA20"] and latest["RSI"] >= 55:
                    stock = symbol.replace(".NS", "")
                    msg = f"🚀 *ALADIN AI ALERT*\n\n📌 *Stock:* {stock}\n💰 *Price:* ₹{round(latest['Close'], 2)}\n📊 *RSI:* {round(latest['RSI'], 1)}"
                    send_alert(msg)
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        time.sleep(300)  # Scan every 5 minutes


@app.route("/")
def home():
    return "ALADIN AI Analytics Engine is Running 24x7!"


if __name__ == "__main__":
    Thread(target=run_analytics_loop).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
