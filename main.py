from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# कुछ पॉपुलर स्टॉक्स की लिस्ट जिन पर डैशबोर्ड नजर रखेगा
DEFAULT_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALADIN AI Analytics Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #2c3e50; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .footer { text-align: center; margin-top: 20px; font-size: 0.9em; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ALADIN AI Analytics Dashboard</h1>
        <p style="text-align: center; color: #555;">Real-time Stock Market Tracking & AI Engine</p>
        <table>
            <thead>
                <tr>
                    <th>Stock Symbol</th>
                    <th>Current Price (₹)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in stock_data %}
                <tr>
                    <td><strong>{{ stock.symbol }}</strong></td>
                    <td>₹{{ stock.price }}</td>
                    <td style="color: green;">{{ stock.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="footer">
            <p>Running 24x7 on Render 🚀</p>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    stock_data = []
    for ticker in DEFAULT_STOCKS:
        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period="1d")
            if not todays_data.empty:
                price = round(todays_data['Close'].iloc[-1], 2)
                stock_data.append({"symbol": ticker, "price": price, "status": "Active / Live"})
            else:
                stock_data.append({"symbol": ticker, "price": "N/A", "status": "No Data"})
        except Exception as e:
            stock_data.append({"symbol": ticker, "price": "Error", "status": str(e)})

    return render_template_string(HTML_TEMPLATE, stock_data=stock_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

