import yfinance as yf
import pandas as pd
import json

def load_holdings(path="data/holdings.json"):
    with open(path, "r") as f:
        return json.load(f)

def save_holdings(holdings, path="data/holdings.json"):
    with open(path, "w") as f:
        json.dump(holdings, f, indent=2)

def get_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def calculate_returns(df):
    df["daily_return"] = df["Close"].pct_change()
    df["cumulative_return"] = (1 + df["daily_return"]).cumprod() - 1
    return df

def get_portfolio_value(holdings):
    portfolio = {}

    for ticker, info in holdings.items():
        try:
            shares = info["shares"]
            buy_price = info["buy_price"]

            data = get_stock_data(ticker)
            data = calculate_returns(data)

            latest_price = data["Close"].iloc[-1]
            cumulative_return = data["cumulative_return"].iloc[-1]

            gain_loss = round((latest_price - buy_price) * shares, 2)
            gain_loss_pct = round(((latest_price - buy_price) / buy_price) * 100, 2)

            portfolio[ticker] = {
                "shares": shares,
                "buy_price": round(buy_price, 2),
                "current_price": round(latest_price, 2),
                "current_value": round(latest_price * shares, 2),
                "cost_basis": round(buy_price * shares, 2),
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct,
                "cumulative_return": round(cumulative_return * 100, 2),
                "daily_returns": data["daily_return"].dropna()
            }

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue

    return portfolio