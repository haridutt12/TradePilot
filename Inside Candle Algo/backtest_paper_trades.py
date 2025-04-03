import pandas as pd
import os
from Dhan_Tradehull_V2 import Tradehull
import datetime
from dotenv import load_dotenv
import pdb

load_dotenv()

def backtest_signals(csv_file):
    """
    Backtest trading signals stored in the CSV file using their respective timeframes.
    """
    if not os.path.exists(csv_file):
        print("No trades to backtest.")
        return

    # Load the signals
    trades = pd.read_csv(csv_file)
    # trades['Timestamp'] = pd.to_datetime(trades['Timestamp'])
    trades['Timestamp'] = pd.to_datetime(trades['Timestamp'], format='mixed', dayfirst=True)

    tsl = Tradehull(os.getenv("CLIENT_CODE"), os.getenv("TOKEN_ID"))
    
    results = []
    count = 0
    for _, trade in trades.iterrows():
        stock = trade['Stock Name']
        action = trade['Action']
        entry_price = float(trade['Entry Price'])
        target = float(trade['Target Profit'])
        stop_loss = float(trade['Stop Loss'])
        entry_time = trade['Timestamp']
        timeframe = str(trade['Timeframe'])  # Use the timeframe from the trade data
        count += 1
        print(f"Backtesting {stock} in {timeframe}-minute timeframe, total trades count {count}")
        
        # Fetch historical data after the trade entry time
        data = tsl.get_historical_data(stock, 'NSE', timeframe)
        data.index = pd.to_datetime(data.timestamp)
        data.index = data.index.tz_convert(None)  # Removes timezone information
        if data is None or data.empty:
            print(f"Skipping {stock} for {timeframe}-minute timeframe due to missing data.")
            continue
        
        # Filter data from trade entry time onward
        data = data[data.index >= entry_time]
        
        trade_outcome = "Open"
        exit_price = None
        exit_time = None
        for index, row in data.iterrows():
            high = row['high']
            low = row['low']
            
            if action == "BUY":
                if high >= target:
                    trade_outcome = "Win"
                    exit_price = target
                    exit_time = index
                    break
                elif low <= stop_loss:
                    trade_outcome = "Loss"
                    exit_price = stop_loss
                    exit_time = index
                    break
            elif action == "SELL":
                if low <= target:
                    trade_outcome = "Win"
                    exit_price = target
                    exit_time = index
                    break
                elif high >= stop_loss:
                    trade_outcome = "Loss"
                    exit_price = stop_loss
                    exit_time = index
                    break
        
        results.append({
            "Stock": stock,
            "Action": action,
            "Entry Price": entry_price,
            "Exit Price": exit_price,
            "Outcome": trade_outcome,
            "Entry Time": entry_time,
            "Exit Time": exit_time,
            "Timeframe": timeframe
        })
    
    results_df = pd.DataFrame(results)
    print(results_df)
    results_df.to_csv("results_inside_candle_paper_trades.csv", index=False)
    print("Backtesting complete. Results saved to backtest_results.csv")

if __name__ == "__main__":
    backtest_signals("inside_candle_paper_trades.csv")
