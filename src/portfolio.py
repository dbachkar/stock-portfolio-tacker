import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template_string, request

app=Flask(__name__)

def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    hist= stock.history(period=period)
    return hist

def calculate_returns(df):
    df['daily_return']= df['Close'].pct_change()
    df['cumulative_return']=(1+df['daily_return']).cumprod()-1
    return df

def get_portfolio_value(holdings):
    portfolio={}

    for ticker, shares in holdings.items():
        data= get_stock_data(ticker)
        data=calculate_returns(data)

        latest_price=data["Close"].iloc[-1]
        cumulative_return=data['cumulative_return'].iloc[-1]

        portfolio[ticker]={
            'shares': shares,
            'current_price': round(latest_price, 2),
            'current_value': round(float(latest_price)*float(shares), 2),
            'cumulative_return': round(cumulative_return*100, 2)
        }
    return portfolio

def generate_chart(holdings):
    plt.figure(figsize=(12,6))

    for ticker in holdings:
        data=get_stock_data(ticker)
        data=calculate_returns(data)
        plt.plot(data.index, data['cumulative_return']*100, label=ticker)

    plt.title("Cumulative Return Over the Past Year")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf=io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data=base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return chart_data

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Portfolio Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f4f4f4; }
        input { padding: 8px; margin: 4px; width: 150px; }
        button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .total { font-weight: bold; font-size: 1.2em; margin: 10px 0; }
        .stock-row { display: flex; gap: 10px; margin: 8px 0; align-items: center; }
        .remove-btn { background: #e74c3c; padding: 6px 12px; }
    </style>
</head>
<body>
    <h1>📊 Stock Portfolio Tracker</h1>
    
    <form method="POST">
        <div id="stocks">
            {% for i in range(num_stocks) %}
            <div class="stock-row">
                <input type="text" name="ticker" placeholder="Ticker (e.g. AAPL)" 
                       value="{{ tickers[i] if tickers else '' }}">
                <input type="number" name="shares" placeholder="Shares" step="0.01"
                       value="{{ shares_list[i] if shares_list else '' }}">
            </div>
            {% endfor %}
        </div>
        <br>
        <button type="submit" name="action" value="add_row">+ Add Stock</button>
        <button type="submit" name="action" value="track">Track Portfolio</button>
    </form>

    {% if portfolio %}
        <h2>Portfolio Summary</h2>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Shares</th>
                <th>Current Price</th>
                <th>Current Value</th>
                <th>1Y Return</th>
            </tr>
            {% for ticker, info in portfolio.items() %}
            <tr>
                <td>{{ ticker }}</td>
                <td>{{ info.shares }}</td>
                <td>${{ "%.2f"|format(info.current_price) }}</td>
                <td>${{ info.current_value }}</td>
                <td>{{ info.cumulative_return }}%</td>
            </tr>
            {% endfor %}
        </table>
        <p class="total">Total Portfolio Value: ${{ total_value }}</p>
        
        <h2>Cumulative Returns Chart</h2>
        <img src="data:image/png;base64,{{ chart }}" width="100%">
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    portfolio = None
    chart = None
    total_value = 0
    tickers = []
    shares_list = []
    num_stocks = 3  

    if request.method == "POST":
        action = request.form.get("action")
        tickers = request.form.getlist("ticker")
        shares_list = request.form.getlist("shares")
        num_stocks = len(tickers)

        if action == "add_row":
            num_stocks += 1

        elif action == "track":
            holdings = {}
            for ticker, shares in zip(tickers, shares_list):
                ticker = ticker.strip().upper()
                if ticker and shares:
                    try:
                        holdings[ticker] = float(shares)
                    except ValueError:
                        continue

            if holdings:
                portfolio = get_portfolio_value(holdings)
                total_value = round(sum(info["current_value"] for info in portfolio.values()), 2)
                chart = generate_chart(holdings)

    return render_template_string(
        HTML_TEMPLATE,
        portfolio=portfolio,
        chart=chart,
        total_value=total_value,
        num_stocks=num_stocks,
        tickers=tickers,
        shares_list=shares_list
    )

if __name__ == "__main__":
    app.run(debug=True)



