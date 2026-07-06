import numpy as np

def sharpe_ratio(daily_returns, risk_free_rate=0.05):
    excess_returns = daily_returns - risk_free_rate / 252
    return round(excess_returns.mean() / excess_returns.std() * (252 ** 0.5), 2)

def daily_volatility(daily_returns):
    return round(daily_returns.std() * 100, 2)

def annualized_volatility(daily_returns):
    return round(daily_returns.std() * (252 ** 0.5) * 100, 2)

def max_drawdown(daily_returns):
    cumulative = (1 + daily_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return round(drawdown.min() * 100, 2)

def get_all_metrics(daily_returns):
    return {
        "sharpe_ratio": sharpe_ratio(daily_returns),
        "daily_volatility": daily_volatility(daily_returns),
        "annualized_volatility": annualized_volatility(daily_returns),
        "max_drawdown": max_drawdown(daily_returns)
    }