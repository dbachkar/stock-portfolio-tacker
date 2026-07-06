import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from src.modified_portfolio import get_stock_data, calculate_returns

def generate_chart(holdings_data):
    plt.figure(figsize=(12, 6))

    for ticker, info in holdings_data.items():
        data = get_stock_data(ticker)
        data = calculate_returns(data)
        plt.plot(data.index, data["cumulative_return"] * 100, label=ticker)

    # SPY benchmark line
    spy_data = get_stock_data("SPY")
    spy_data = calculate_returns(spy_data)
    plt.plot(
        spy_data.index,
        spy_data["cumulative_return"] * 100,
        label="S&P 500",
        linestyle="--",
        color="black",
        linewidth=2
    )

    plt.title("Cumulative Return Over the Past Year")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return chart_data