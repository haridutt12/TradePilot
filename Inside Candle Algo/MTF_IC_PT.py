import pdb
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
import talib
import datetime
import os
import csv
import json
import time
from dotenv import load_dotenv
import multiprocessing

load_dotenv()
client_code = os.getenv("CLIENT_CODE")
token_id = os.getenv("TOKEN_ID")
tsl = Tradehull(client_code, token_id)
available_balance = tsl.get_balance()
leveraged_margin = available_balance * 5

# ---------------------Input Window Start-------------------------#
max_trades = 1
max_retries = 3
per_trade_margin = leveraged_margin / max_trades
atr_multiplier_sl = 1.5  # Stop Loss (1.5x ATR)
atr_multiplier_tp = 2.0  # Take Profit (2x ATR)

nifty50_watchlist = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", 
                     "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL", 
                     "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT", 
                     "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", 
                     "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", 
                     "KOTAKBANK", "LTIM", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", 
                     "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA", 
                     "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", 
                     "ULTRACEMCO", "UPL", "WIPRO"]
watchlist = nifty50_watchlist
# ---------------------Input Window End---------------------------#

csv_file = "inside_candle_paper_trades.csv"

def ensure_headers():
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists or os.stat(csv_file).st_size == 0:
            file.seek(0)
            writer.writerow(["Stock Name", "Action", "Entry Price", "Target Profit", "Stop Loss", "Timeframe", "Timestamp"])

if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Stock Name", "Action", "Entry Price", "Target Profit", "Stop Loss", "Timeframe", "Timestamp"])

def log_signal(stock_name, action, entry_price, target_profit, stop_loss, timeframe, timestamp):
    ensure_headers()
    # Check for duplicate entry by reading the last row of the CSV
    duplicate = False
    if os.path.exists(csv_file) and os.stat(csv_file).st_size > 0:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = list(csv.reader(file))
            if len(reader) > 1:
                last_row = reader[-1]
                if last_row[0] == stock_name and last_row[1] == action and float(last_row[2]) == float(entry_price):
                    duplicate = True

    if duplicate:
        print(f"Skipping duplicate signal for {stock_name} ({action} at {entry_price})")
        return

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([stock_name, action, entry_price, target_profit, stop_loss, timeframe, timestamp])
    print(f"Logged signal: {stock_name} {action} at {entry_price}")

def get_tick_size(price: float) -> float:
    if price < 250:
        return 0.01
    elif price <= 1000:
        return 0.05
    elif price <= 5000:
        return 0.10
    elif price <= 10000:
        return 0.50
    elif price <= 20000:
        return 1.00
    else:
        return 5.00

def trading_loop(timeframe_in_min):
    count = 0
    traded_watchlist = []
    while True:
        for stock_name in watchlist:
            start_time = time.time()
            for attempt in range(max_retries):
                try:
                    chart = tsl.get_historical_data(stock_name, 'NSE', timeframe_in_min)
                    if not isinstance(chart, pd.DataFrame) or chart.empty:
                        print(f"Skipping {stock_name} due to missing data (DH-907 Error)")
                        chart = None
                    break
                except Exception as e:
                    print(f"Error fetching data for {stock_name} on attempt {attempt+1}/{max_retries}: {e}")
                    time.sleep(2)
                    chart = None
            if chart is None:
                continue

            end_time = time.time()
            fetch_data_time = end_time - start_time
            # print(f"[{timeframe_in_min}] Time taken for fetching historical data for {stock_name}: {fetch_data_time:.4f} seconds")

            start_time = time.time()
            count += 1
            chart['rsi'] = talib.RSI(chart['close'], timeperiod=14)
            chart['ATR'] = talib.ATR(chart['high'], chart['low'], chart['close'], timeperiod=14)
            if len(chart) < 4:
                continue
            bc = chart.iloc[-2]
            ic = chart.iloc[-3]
            ba_c = chart.iloc[-4]
            uptrend = bc['rsi'] > 50
            downtrend = bc['rsi'] < 49
            inside_candle_formed = (ba_c['high'] > ic['high']) and (ba_c['low'] < ic['low'])
            upper_side_breakout = bc['high'] > ba_c['high']
            down_side_breakout = bc['low'] < ba_c['low']
            no_repeat_order = stock_name not in traded_watchlist
            max_order_limit = len(traded_watchlist) <= max_trades
            atr_value = round(chart.iloc[-1]['ATR'], 2)
            end_time = time.time()
            indicator_calc_time = end_time - start_time
            # print(f"[{timeframe_in_min}] Time taken for indicator calculations for {stock_name}: {indicator_calc_time:.4f} seconds")

            if uptrend and inside_candle_formed and upper_side_breakout:
                entry_price = bc['close']
                tick_size = get_tick_size(entry_price)
                trigger_price = entry_price - 2 * tick_size
                abs_stop_loss = round(((atr_multiplier_sl * atr_value) // tick_size) * tick_size, 2)
                abs_target_profit = round(((atr_multiplier_tp * atr_value) // tick_size) * tick_size, 2)
                qty = 1
                print(f"[{timeframe_in_min}] {stock_name} BUY at {entry_price}, TP: {abs_target_profit}, SL: {abs_stop_loss}, Time: {datetime.datetime.now()}")
                # tsl.order_placement(stock_name, 'NSE', qty, entry_price, trigger_price, "LIMIT", "BUY", "BO",
                #                     bo_profit_value=abs_target_profit, bo_stop_loss_Value=abs_stop_loss)
                log_signal(stock_name, "BUY", entry_price, entry_price+abs_target_profit, entry_price-abs_stop_loss, timeframe_in_min, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                traded_watchlist.append(stock_name)

            if downtrend and inside_candle_formed and down_side_breakout:
                entry_price = bc['close']
                tick_size = get_tick_size(entry_price)
                trigger_price = entry_price + 2 * tick_size
                abs_stop_loss = round(((atr_multiplier_sl * atr_value) // tick_size) * tick_size, 2)
                abs_target_profit = round(((atr_multiplier_tp * atr_value) // tick_size) * tick_size, 2)
                qty = 1
                print(f"[{timeframe_in_min}] {stock_name} SELL at {entry_price}, TP: {abs_target_profit}, SL: {abs_stop_loss}, Time: {datetime.datetime.now()}")
                # tsl.order_placement(stock_name, 'NSE', qty, entry_price, trigger_price, "LIMIT", "SELL", "BO",
                #                     bo_profit_value=abs_target_profit, bo_stop_loss_Value=abs_stop_loss)
                log_signal(stock_name, "SELL", entry_price, entry_price-abs_target_profit, entry_price+abs_stop_loss, timeframe_in_min, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                traded_watchlist.append(stock_name)
 
            print(f"[{timeframe_in_min}] Scanned {stock_name}, count: {count}, Time: {datetime.datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    # Define the list of timeframes you want to run concurrently
    timeframes = ['1','5','15','25','60']  # example timeframes in minutes

    processes = []
    for tf in timeframes:
        p = multiprocessing.Process(target=trading_loop, args=(tf,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
