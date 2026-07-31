from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import ta
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)

DEFAULT_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS"]
TELEGRAM_BOT_TOKEN = "8728680154:AAHMZw_KD4XWHTMoTAozEqd3nmkPKiMDBYk"
CHAT_ID = "8596188242"

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram Error:", e)

def fetch_and_analyze_stocks():
    stock_data = []
    telegram_msg = "🚀 *ALADIN AI Pro - Market Intelligence & Volume Alert* 🚀\n\n"
    
    for ticker in DEFAULT_STOCKS:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")
            if not df.empty and len(df) > 10:
                current_price = round(df['Close'].iloc[-1], 2)
                
                # टेक्निकल इंडिकेटर्स (RSI निकालना)
                rsi_series = ta.momentum.rsi(df['Close'], window=14)
                current_rsi = round(rsi_series.iloc[-1], 2) if not rsi_series.empty else 50
                
                # वॉल्यूम स्पाइक (Volume Spike) डिटेक्शन लॉजिक
                avg_volume = df['Volume'].rolling(window=10).mean().iloc[-2] if len(df) > 10 else df['Volume'].mean()
                today_volume = df['Volume'].iloc[-1]
                
                if today_volume > (avg_volume * 1.5):
                    volume_status = "🚨 High Volume Spike! (Smart Money Active)"
                    vol_class = "spike"
                else:
                    volume_status = "Normal Volume ⚖️"
                    vol_class = ""
                
                # मशीन लर्निंग प्रिडिक्शन (Linear Regression)
                df['Day'] = np.arange(len(df))
                X = df[['Day']]
                y = df['Close']
                
                model = LinearRegression()
                model.fit(X, y)
                
                next_day = np.array([[len(df)]])
                predicted_price = round(model.predict(next_day)[0], 2)
                
                if predicted_price >= current_price:
                    status = "Bullish / Up 📈"
                    trend_class = "up"
                else:
                    status = "Bearish / Down 📉"
                    trend_class = "down"
                    
                rsi_signal = "Overbought ⚠️" if current_rsi > 70 else ("Oversold 🟢" if current_rsi < 30 else "Neutral ⚖️")
                
                stock_data.append({
                    "symbol": ticker, 
                    "price": current_price, 
                    "predicted_price": predicted_price,
                    "rsi": current_rsi,
                    "rsi_signal": rsi_signal,
                    "volume_status": volume_status,
                    "vol_class": vol_class,
                    "status": status,
                    "trend_class": trend_class
                })
                
                telegram_msg += f"📌 *{ticker}*\n💰 Current: ₹{current_price}\n🎯 Target: ₹{predicted_price}\n📊 RSI: {current_rsi} ({rsi_signal})\n🔍 Vol: {volume_status}\nTrend: {status}\n\n"
            else:
                stock_data.append({
                    "symbol": ticker, "price": "N/A", "predicted_price": "N/A", 
                    "rsi": "N/A", "rsi_signal": "N/A", "volume_status": "N/A", "vol_class": "", "status": "No Data", "trend_class": ""
                })
        except Exception as e:
            stock_data.append({
                "symbol": ticker, "price": "Error", "predicted_price": "Error", 
                "rsi": "Error", "rsi_signal": "Error", "volume_status": "Error", "vol_class": "", "status": str(e), "trend_class": ""
            })
            
    return stock_data, telegram_msg

def scheduled_job():
    _, msg = fetch_and_analyze_stocks()
    send_telegram_message("⏰ *Automated Market Scan*\n\n" + msg)

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_job, trigger="interval", hours=6)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALADIN AI Pro Analytics Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1050px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #2c3e50; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .footer { text-align: center; margin-top: 20px; font-size: 0.9em; color: #777; }
        .up { color: green; font-weight: bold; }
        .down { color: red; font-weight: bold; }
        .spike { color: #d35400; font-weight: bold; background-color: #f39c1220; padding: 4px 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ALADIN AI Pro Analytics Dashboard</h1>
        <p style="text-align: center; color: #555;">AI Price Prediction, RSI Indicators & Institutional Volume Spike Detector</p>
        <table>
            <thead>
                <tr>
                    <th>Stock Symbol</th>
                    <th>Current Price (₹)</th>
                    <th>AI Target (₹)</th>
                    <th>RSI Indicator</th>
                    <th>Volume Activity</th>
                    <th>Trend Status</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in stock_data %}
                <tr>
                    <td><strong>{{ stock.symbol }}</strong></td>
                    <td>₹{{ stock.price }}</td>
                    <td>₹{{ stock.predicted_price }}</td>
                    <td>{{ stock.rsi }} ({{ stock.rsi_signal }})</td>
                    <td><span class="{{ stock.vol_class }}">{{ stock.volume_status }}</span></td>
                    <td class="{{ stock.trend_class }}">{{ stock.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="footer">
            <p>Running 24x7 on Render | Advanced AI Market Intelligence 🚀</p>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    stock_data, telegram_msg = fetch_and_analyze_stocks()
    send_telegram_message(telegram_msg)
    return render_template_string(HTML_TEMPLATE, stock_data=stock_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
