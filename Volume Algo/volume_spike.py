import pdb
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
import datetime
import os
import csv
import time
from dotenv import load_dotenv
import talib  # Ensure TA-Lib is installed

# Load environment variables and initialize the Tradehull API
load_dotenv()
client_code = os.getenv("CLIENT_CODE")
token_id = os.getenv("TOKEN_ID")
tsl = Tradehull(client_code, token_id)
available_balance = tsl.get_balance()
leveraged_margin = available_balance * 5

# ---------------------Input Window Start-------------------------#
timeframe_in_min = 'DAY'  # timeframe for volume analysis (in minutes)
max_retries = 3
volume_window = 20         # periods over which to calculate the average volume
vol_multiplier = 1.5       # volume ratio threshold
rsi_upper_threshold = 50   # bullish momentum threshold
rsi_lower_threshold = 49   # bearish momentum threshold

# Define your watchlist (using nifty50 as an example)
nifty50_watchlist = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", 
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL", 
    "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT", 
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", 
    "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", 
    "KOTAKBANK", "LTIM", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", 
    "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA", 
    "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", 
    "ULTRACEMCO", "UPL", "WIPRO"
]
watchlist = nifty50_watchlist
# ---------------------Input Window End---------------------------#

# CSV file to log high volume signals
csv_file = "institutional_high_volume_signals.csv"

def ensure_headers():
    """
    Ensure that the CSV file exists with proper headers.
    Headers include stock name, current volume, average volume,
    volume ratio, RSI, timeframe, and timestamp.
    """
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write headers if file is new or empty
        if not file_exists or os.stat(csv_file).st_size == 0:
            writer.writerow(["Stock Name", "Current Volume", "Avg Volume", "Volume Ratio", "RSI", "Timeframe", "Timestamp"])

def log_signal(stock_name, current_vol, avg_vol, vol_ratio, rsi, timeframe):
    """
    Log a high volume signal along with RSI reading to the CSV file.
    """
    ensure_headers()
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            stock_name,
            current_vol,
            avg_vol,
            vol_ratio,
            rsi,
            timeframe,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
    print(f"Logged signal for {stock_name}: Current Vol = {current_vol}, Avg Vol = {avg_vol:.2f}, Ratio = {vol_ratio:.2f}, RSI = {rsi:.2f}")

def volume_strategy(timeframe_in_min, volume_window=20, vol_multiplier=2.0):
    """
    Run the high volume strategy on a given timeframe.
    A signal is logged if the current volume is at least `vol_multiplier`
    times the average volume over `volume_window` periods, and the RSI confirms strong momentum:
      - RSI >= rsi_upper_threshold for bullish signals, or
      - RSI <= rsi_lower_threshold for bearish signals.
    """
    count = 0
    while True:
        for stock_name in watchlist:
            chart = None
            start_time = time.time()
            # Retry logic for data fetching
            for attempt in range(max_retries):
                try:
                    chart = tsl.get_historical_data(stock_name, 'NSE', timeframe_in_min)
                    # Check if chart is a valid DataFrame with required columns
                    if not isinstance(chart, pd.DataFrame) or chart.empty or 'volume' not in chart.columns or 'close' not in chart.columns:
                        print(f"Skipping {stock_name} due to missing data.")
                        chart = None
                    break
                except Exception as e:
                    print(f"Error fetching data for {stock_name} on attempt {attempt+1}/{max_retries}: {e}")
                    time.sleep(2)
                    chart = None
            if chart is None:
                continue

            fetch_time = time.time() - start_time
            print(f"[{timeframe_in_min}] Fetched data for {stock_name} in {fetch_time:.4f} seconds.")

            # Ensure we have enough data points to calculate average volume and RSI
            if len(chart) < volume_window:
                print(f"Not enough data for {stock_name} to calculate average volume and RSI.")
                continue

            # Calculate rolling average volume over the defined window
            chart['AvgVolume'] = chart['volume'].rolling(window=volume_window).mean()
            # Calculate RSI with time period 14
            chart['RSI'] = talib.RSI(chart['close'], timeperiod=14)

            current_volume = chart.iloc[-1]['volume']
            avg_volume = chart.iloc[-1]['AvgVolume']
            current_rsi = chart.iloc[-1]['RSI']

            # Skip if average volume or RSI is not available
            if pd.isna(avg_volume) or avg_volume == 0 or pd.isna(current_rsi):
                continue

            vol_ratio = current_volume / avg_volume
            print(f"[{timeframe_in_min}] {stock_name}: Current Vol = {current_volume}, Avg Vol = {avg_volume:.2f}, Ratio = {vol_ratio:.2f}, RSI = {current_rsi:.2f}")

            # Check if the volume spike meets our threshold and RSI confirms momentum:
            # For bullish signals (potential buying), require RSI >= rsi_upper_threshold.
            # For bearish signals (potential selling), require RSI <= rsi_lower_threshold.
            if vol_ratio >= vol_multiplier:
                if current_rsi >= rsi_upper_threshold:
                    print(f"[{timeframe_in_min}] Bullish high volume signal for {stock_name}.")
                    log_signal(stock_name, current_volume, avg_volume, vol_ratio, current_rsi, timeframe_in_min)
                elif current_rsi <= rsi_lower_threshold:
                    print(f"[{timeframe_in_min}] Bearish high volume signal for {stock_name}.")
                    log_signal(stock_name, current_volume, avg_volume, vol_ratio, current_rsi, timeframe_in_min)
                else:
                    print(f"[{timeframe_in_min}] Volume spike detected for {stock_name} but RSI ({current_rsi:.2f}) is not extreme enough.")

            count += 1
            print(f"[{timeframe_in_min}] Scanned {stock_name}, count: {count}, Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Sleep briefly before scanning the watchlist again
        time.sleep(1)

if __name__ == "__main__":
    volume_strategy(timeframe_in_min, volume_window, vol_multiplier)
