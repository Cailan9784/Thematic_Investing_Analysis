import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from yfinance import download
from matplotlib.ticker import PercentFormatter

# --------------------------
# Create Output Folders
# --------------------------

os.makedirs("charts", exist_ok=True)
os.makedirs("data", exist_ok=True)


tickers = ["NVDA", "PLTR", "SNDK", "COHR", "LNG", "CEG", "CCJ", "LLY", "UTHR", "RKLB", "ASTS" , "VOO"]
data = download(tickers, start="2020-01-01")
#data = data.reset_index().melt(id_vars="Date" , var_name="Ticker" , value_name="Price")

downloaded_tickers = len(data["Close"].columns)

print(f"\nDownloaded tickers: {downloaded_tickers}/{len(tickers)}")

prices = data["Close"]
returns = prices.pct_change(fill_method=None)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

ai = ["NVDA" , "PLTR" , "SNDK" , "COHR"]
energy= ["LNG" , "CEG" , "CCJ"]
biotech = ["LLY" , "UTHR"]
space = ["RKLB" , "ASTS"]
theme_returns = pd.DataFrame()

theme_returns["AI"] = returns[ai].mean(axis=1)
theme_returns["Energy"] = returns[energy].mean(axis=1)
theme_returns["Biotech"] = returns[biotech].mean(axis=1)
theme_returns["Space"] = returns[space].mean(axis=1)
theme_returns["VOO"] = returns["VOO"]

# Keep only dates where all themes and VOO have returns
theme_returns = theme_returns.dropna()

print("Analysis start date:", theme_returns.index.min())
print("Analysis end date:", theme_returns.index.max())
print("Number of observations:", len(theme_returns))

print(theme_returns.head())
print(theme_returns.describe())

cumulative_returns = (1 + theme_returns).cumprod()

cumulative_returns.plot(figsize=(12, 6))
plt.title("Growth of $1 Invested: Themes vs. VOO")
plt.xlabel("Date")
plt.ylabel("Investment Value")
plt.savefig("charts/growth_of_1_dollar.png", dpi=300, bbox_inches="tight")
plt.show()

print("data length:", len(data))
print("returns length:", len(returns))
print("\ndata index:")
print(data.index)

# --------------------------
# Full-History Performance Summary
# --------------------------

trading_days = 252

total_return = (1 + theme_returns).prod() - 1

years = len(theme_returns) / trading_days
annualized_return = (1 + total_return) ** (1 / years) - 1

annualized_volatility = theme_returns.std() * np.sqrt(trading_days)

# Sharpe ratio assumes a 0% risk-free rate

sharpe_ratio = annualized_return / annualized_volatility

performance_summary = pd.DataFrame({
    "Total Return": total_return,
    "Annualized Return": annualized_return,
    "Annualized Volatility": annualized_volatility,
    "Sharpe Ratio": sharpe_ratio
})

# --------------------------
# Maximum Drawdown
# --------------------------

running_max = cumulative_returns.cummax()
drawdown = (cumulative_returns - running_max) / running_max
max_drawdown = drawdown.min()

performance_summary["Maximum Drawdown"] = max_drawdown

# --------------------------
# Format Performance Summary
# --------------------------

formatted_summary = performance_summary.copy()

percentage_columns = [
    "Total Return",
    "Annualized Return",
    "Annualized Volatility",
    "Maximum Drawdown"
]

for column in percentage_columns:
    formatted_summary[column] = formatted_summary[column].map(
        lambda x: f"{x:.2%}"
    )

formatted_summary["Sharpe Ratio"] = formatted_summary["Sharpe Ratio"].map(
    lambda x: f"{x:.2f}"
)

print("\nFull-History Performance Summary")
print("(Sharpe ratio assumes a 0% risk-free rate)")
print(formatted_summary)

# --------------------------
# Theme Constituents Check
# --------------------------

theme_counts = pd.DataFrame()

theme_counts["AI"] = returns[ai].count(axis=1)
theme_counts["Energy"] = returns[energy].count(axis=1)
theme_counts["Biotech"] = returns[biotech].count(axis=1)
theme_counts["Space"] = returns[space].count(axis=1)

print("\nTheme Constituents")
print(theme_counts.head(20))

print("\nFirst date with full theme representation:")

for theme, stocks in {
    "AI": ai,
    "Energy": energy,
    "Biotech": biotech,
    "Space": space
}.items():

    counts = returns[stocks].count(axis=1)
    first_full = counts[counts == len(stocks)].index.min()

    print(f"{theme}: {first_full}")

# --------------------------
# Fixed-Composition Analysis
# --------------------------


common_start = "2025-02-14"

common_returns = returns.loc[common_start:].copy()

fixed_theme_returns = pd.DataFrame(index=common_returns.index)

fixed_theme_returns["AI"] = common_returns[ai].mean(axis=1, skipna=False)
fixed_theme_returns["Energy"] = common_returns[energy].mean(axis=1, skipna=False)
fixed_theme_returns["Biotech"] = common_returns[biotech].mean(axis=1, skipna=False)
fixed_theme_returns["Space"] = common_returns[space].mean(axis=1, skipna=False)
fixed_theme_returns["VOO"] = common_returns["VOO"]

# Require every constituent to have a return
fixed_theme_returns = fixed_theme_returns.dropna()

print("\nFixed-composition analysis period:")
print("Start:", fixed_theme_returns.index.min())
print("End:", fixed_theme_returns.index.max())
print("Observations:", len(fixed_theme_returns))

fixed_total_return = (1 + fixed_theme_returns).prod() - 1
fixed_years = len(fixed_theme_returns) / 252

fixed_annualized_return = (
    (1 + fixed_total_return) ** (1 / fixed_years) - 1
)

fixed_volatility = fixed_theme_returns.std() * np.sqrt(252)

# Sharpe ratio assumes a 0% risk-free rate
fixed_sharpe = fixed_annualized_return / fixed_volatility

fixed_summary = pd.DataFrame({
"Total Return": fixed_total_return,
"Annualized Return": fixed_annualized_return,
"Annualized Volatility": fixed_volatility,
"Sharpe Ratio": fixed_sharpe
})

print("\nFixed-Composition Performance Summary")
print("Sharpe Ratio assumption: 0% risk-free rate")
print(fixed_summary)



# --------------------------
# Correlation Matrix
# --------------------------

correlation_matrix = theme_returns.corr()

print("\nCorrelation Matrix")
print(correlation_matrix)

# --------------------------
# 30-Day Rolling Volatility
# --------------------------

rolling_volatility = (
        theme_returns.rolling(window=30).std()
        * np.sqrt(252)
)

rolling_volatility.plot(figsize=(12, 6))

plt.axhline(
    y=0.20,
    color="black",
    linestyle="--",
    alpha=0.5,
    label="20% Volatility"
)

plt.title("30-Day Rolling Annualized Volatility")
plt.xlabel("Date")
plt.ylabel("Annualized Volatility")

plt.legend()

plt.tight_layout()
plt.savefig("charts/rolling_volatility.png", dpi=300, bbox_inches="tight")
plt.show()

# --------------------------
# Drawdown Through Time
# --------------------------

cumulative_growth = (1 + theme_returns).cumprod()

running_peak = cumulative_growth.cummax()

drawdown_series = (
    cumulative_growth / running_peak
) - 1

drawdown_series.plot(figsize=(12, 6))

plt.title("Drawdown Through Time: Themes vs. VOO")
plt.xlabel("Date")
plt.ylabel("Drawdown")

plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))

plt.axhline(
    y=0,
    color="black",
    linewidth=1
)

plt.legend(title="Theme")
plt.tight_layout()

plt.savefig(
    "charts/drawdown_through_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# --------------------------
# Risk vs. Return Scatter Plot
# --------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    annualized_volatility,
    annualized_return,
    s=100
)

for theme in annualized_return.index:
    plt.text(
        annualized_volatility[theme],
        annualized_return[theme],
        theme,
        fontsize=10,
        ha="left"
    )

plt.title("Risk vs. Return")
plt.xlabel("Annualized Volatility")
plt.ylabel("Annualized Return")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("charts/risk_return_scatter.png", dpi=300, bbox_inches="tight")
plt.show()

# --------------------------
# Calendar-Year Returns
# --------------------------

annual_returns = (
    (1 + theme_returns)
    .groupby(theme_returns.index.year)
    .prod()
    - 1
)

annual_returns.index.name = "Year"

# Label the current partial year as YTD
annual_returns.index = annual_returns.index.astype(str)

annual_returns = annual_returns.rename(
    index={"2026": "2026 YTD"}

)
formatted_annual_returns = annual_returns.map(
    lambda x: f"{x:.2%}"
)

print("\nCalendar-Year Returns")
print(formatted_annual_returns)

# --------------------------
# Annual Returns Bar Chart
# --------------------------

annual_returns.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Calendar-Year Returns by Theme")
plt.xlabel("Year")
plt.ylabel("Return")

# Format y-axis as percentages
plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))

# Make the year labels horizontal
plt.xticks(rotation=0)

plt.axhline(0, color="black", linewidth=1)

plt.legend(title="Theme")
plt.tight_layout()
plt.savefig(
    "charts/annual_return_bar_chart.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# --------------------------
# Export Results
# --------------------------

performance_summary.to_csv("data/performance_summary.csv")

theme_returns.to_csv("data/theme_returns.csv")

rolling_volatility.to_csv("data/rolling_volatility.csv")

correlation_matrix.to_csv("data/correlation_matrix.csv")

annual_returns.to_csv("data/annual_returns.csv")

drawdown_series.to_csv("data/drawdown_series.csv")


print("\nCSV files exported successfully!")
print("Saved to:", os.getcwd())

print("\nFiles found:")
print(os.path.exists("data/performance_summary.csv"))
print(os.path.exists("data/theme_returns.csv"))
print(os.path.exists("data/rolling_volatility.csv"))
print(os.path.exists("data/correlation_matrix.csv"))
print(os.path.exists("data/annual_returns.csv"))
print(os.path.exists("data/drawdown_series.csv"))