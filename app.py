from flask import Flask, render_template, request
from src.modified_portfolio import load_holdings, save_holdings, get_portfolio_value
from src.metrics import get_all_metrics
from src.visualizer import generate_chart
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    portfolio = None
    chart = None
    metrics = {}
    total_value = 0
    total_gain_loss = 0
    tickers = []
    shares_list = []
    buy_prices = []
    num_stocks = 3

    if request.method == "POST":
        action = request.form.get("action")
        tickers = request.form.getlist("ticker")
        shares_list = request.form.getlist("shares")
        buy_prices = request.form.getlist("buy_price")
        num_stocks = len(tickers)

        if action == "add_row":
            num_stocks += 1

        elif action in ("track", "save"):
            # build holdings dictionary from form
            holdings = {}
            for ticker, shares, buy_price in zip(tickers, shares_list, buy_prices):
                ticker = ticker.strip().upper()
                if ticker and shares and buy_price:
                    try:
                        holdings[ticker] = {
                            "shares": float(shares),
                            "buy_price": float(buy_price)
                        }
                    except ValueError:
                        continue

            if action == "save" and holdings:
                save_holdings(holdings)
                print("Portfolio saved to data/holdings.json")

            if holdings:
                portfolio = get_portfolio_value(holdings)

                for ticker, info in portfolio.items():
                    metrics[ticker] = get_all_metrics(info["daily_returns"])

                total_value = round(sum(info["current_value"] for info in portfolio.values()), 2)
                total_gain_loss = round(sum(info["gain_loss"] for info in portfolio.values()), 2)
                chart = generate_chart(holdings)

    return render_template(
        "index.html",
        portfolio=portfolio,
        chart=chart,
        metrics=metrics,
        total_value=total_value,
        total_gain_loss=total_gain_loss,
        num_stocks=num_stocks,
        tickers=tickers,
        shares_list=shares_list,
        buy_prices=buy_prices
    )

if __name__ == "__main__":
    app.run(debug=True)