import pandas as pd
import yfinance as yf
import ta
import pdb

# NIFTY 50 Stocks (NSE Tickers)
nifty50_stocks = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", 
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", 
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", 
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", 
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", 
    "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS", "LT.NS", 
    "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", 
    "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", 
    "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", 
    "UPL.NS", "WIPRO.NS"
]

# Strategy Parameters
rsi_period = 14
max_trades = 3
leverage = 5
initial_cash = 100000  # ₹1,00,000 starting capital
per_trade_margin = (initial_cash * leverage) / max_trades

# Function to fetch stock data
def get_stock_data(symbol, period="5y"):
    df = yf.download(symbol, period=period, interval="1d")
    df.columns = df.columns.get_level_values(0)  # Remove multi-index columns
    df.columns.name = None  # Remove the column index name
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=rsi_period).rsi()
    df.dropna(inplace=True)  # Drop NaN values
    return df

# Backtesting function (Vectorized)
def backtest_strategy(stock_data, stock_name):
    global cash, trades_open
    cash = initial_cash
    trades_open = 0
    positions = []

    # Compute Inside Candle Setup
    stock_data["Base_Close"] = stock_data["Close"].shift(4)
    stock_data["Base_High"] = stock_data["High"].shift(4)
    stock_data["Base_Low"] = stock_data["Low"].shift(4)
    stock_data["Inside_High"] = stock_data["High"].shift(3)
    stock_data["Inside_Low"] = stock_data["Low"].shift(3)
    stock_data["Breakout_High"] = stock_data["High"].shift(2)
    stock_data["Breakout_Low"] = stock_data["Low"].shift(2)
    stock_data["Breakout_Close"] = stock_data["Close"].shift(2)
    stock_data["RSI"] = stock_data["RSI"].shift(2)

    # Conditions for Inside Candle & Trends
    stock_data["Inside_Candle"] = (stock_data["Base_High"] > stock_data["Inside_High"]) & (stock_data["Base_Low"] < stock_data["Inside_Low"])
    stock_data["Uptrend"] = stock_data["RSI"] > 50
    stock_data["Downtrend"] = stock_data["RSI"] < 49

    # Buy & Sell Conditions
    stock_data["Buy_Signal"] = (stock_data["Inside_Candle"]) & (stock_data["Uptrend"]) & (stock_data["Breakout_High"] > stock_data["Inside_High"])
    stock_data["Sell_Signal"] = (stock_data["Inside_Candle"]) & (stock_data["Downtrend"]) & (stock_data["Breakout_Low"] < stock_data["Inside_Low"])
    # pdb.set_trace()
    # Vectorized Trade Execution
    buy_trades = stock_data[stock_data["Buy_Signal"]]
    sell_trades = stock_data[stock_data["Sell_Signal"]]

    for date, trade in buy_trades.iterrows():
        if trades_open < max_trades:
            qty = int(per_trade_margin / trade["Breakout_Close"])
            cash -= qty * trade["Breakout_Close"]
            trades_open += 1
            positions.append((qty, trade["Breakout_Close"]))
            print(f"BUY {stock_name} at ₹{trade['Breakout_Close']:.2f} on {date.date()}")

    for date, trade in sell_trades.iterrows():
        if trades_open < max_trades:
            qty = int(per_trade_margin / trade["Breakout_Close"])
            cash += qty * trade["Breakout_Close"]
            trades_open += 1
            positions.append((-qty, trade["Breakout_Close"]))
            print(f"SELL {stock_name} at ₹{trade['Breakout_Close']:.2f} on {date.date()}")

    # Final Portfolio Value Calculation
    final_value = cash + sum(qty * stock_data.iloc[-1]["Close"] for qty, _ in positions)
    return final_value

# Run Backtest for All NIFTY 50 Stocks
final_values = {stock: backtest_strategy(get_stock_data(stock), stock) for stock in nifty50_stocks}

# Print Results
print("\nFinal Portfolio Values:")
for stock, value in final_values.items():
    print(f"{stock}: ₹{value:.2f}")
