import pdb
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
import talib
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
client_code = os.getenv("CLIENT_CODE")
token_id = os.getenv("TOKEN_ID")
tsl = Tradehull(client_code,token_id)

available_balance = tsl.get_balance()
leveraged_margin  = available_balance*5
max_trades = 3
per_trade_margin = (leveraged_margin/max_trades)
atr_multiplier_sl = 1.5  # Stop Loss (1.5x ATR)
atr_multiplier_tp = 2.0  # Take Profit (2x ATR)

watchlist = ['MOTHERSON', 'OFSS', 'MANAPPURAM', 'BSOFT', 'CHAMBLFERT', 'DIXON', 'NATIONALUM', 'DLF', 'IDEA', 'ADANIPORTS', 'SAIL', 'HINDCOPPER', 'INDIGO', 'RECLTD', 'PNB', 'HINDALCO', 'RBLBANK', 'GNFC', 'ALKEM', 'CONCOR', 'PFC', 'GODREJPROP', 'MARUTI', 'ADANIENT', 'ONGC', 'CANBK', 'OBEROIRLTY', 'BANDHANBNK', 'SBIN', 'HINDPETRO', 'CANFINHOME', 'TATAMOTORS', 'LALPATHLAB', 'MCX', 'TATACHEM', 'BHARTIARTL', 'INDIAMART', 'LUPIN', 'INDUSTOWER', 'VEDL', 'SHRIRAMFIN', 'POLYCAB', 'WIPRO', 'UBL', 'SRF', 'BHARATFORG', 'GRASIM', 'IEX', 'BATAINDIA', 'AARTIIND', 'TATASTEEL', 'UPL', 'HDFCBANK', 'LTF', 'TVSMOTOR', 'IOC', 'ABCAPITAL', 'ACC', 'IDFCFIRSTB', 'ABFRL', 'ZYDUSLIFE', 'GLENMARK', 'TATAPOWER', 'PEL', 'LAURUSLABS', 'BANKBARODA', 'KOTAKBANK', 'CUB', 'GAIL', 'DABUR', 'TECHM', 'CHOLAFIN', 'BEL', 'SYNGENE', 'FEDERALBNK', 'NAVINFLUOR', 'AXISBANK', 'LT', 'ICICIGI', 'EXIDEIND', 'TATACOMM', 'RELIANCE', 'ICICIPRULI', 'IPCALAB', 'AUBANK', 'INDIACEM', 'GRANULES', 'HDFCAMC', 'COFORGE', 'LICHSGFIN', 'BAJAJFINSV', 'INFY', 'BRITANNIA', 'M&MFIN', 'BAJFINANCE', 'PIIND', 'DEEPAKNTR', 'SHREECEM', 'INDUSINDBK', 'DRREDDY', 'TCS', 'BPCL', 'PETRONET', 'NAUKRI', 'JSWSTEEL', 'MUTHOOTFIN', 'CUMMINSIND', 'CROMPTON', 'M&M', 'GODREJCP', 'IGL', 'BAJAJ-AUTO', 'HEROMOTOCO', 'AMBUJACEM', 'BIOCON', 'ULTRACEMCO', 'VOLTAS', 'BALRAMCHIN', 'SUNPHARMA', 'ASIANPAINT', 'COALINDIA', 'SUNTV', 'EICHERMOT', 'ESCORTS', 'HAL', 'ASTRAL', 'NMDC', 'ICICIBANK', 'TORNTPHARM', 'JUBLFOOD', 'METROPOLIS', 'RAMCOCEM', 'INDHOTEL', 'HINDUNILVR', 'TRENT', 'TITAN', 'JKCEMENT', 'ASHOKLEY', 'SBICARD', 'BERGEPAINT', 'JINDALSTEL', 'MFSL', 'BHEL', 'NESTLEIND', 'HDFCLIFE', 'COROMANDEL', 'DIVISLAB', 'ITC', 'TATACONSUM', 'APOLLOTYRE', 'AUROPHARMA', 'HCLTECH', 'LTTS', 'BALKRISIND', 'DALBHARAT', 'APOLLOHOSP', 'ABBOTINDIA', 'ATUL', 'UNITDSPR', 'PVRINOX', 'SIEMENS', 'SBILIFE', 'IRCTC', 'GUJGASLTD', 'BOSCHLTD', 'NTPC', 'POWERGRID', 'MARICO', 'HAVELLS', 'MPHASIS', 'COLPAL', 'CIPLA', 'MGL', 'ABB', 'PIDILITIND', 'MRF', 'LTIM', 'PAGEIND', 'PERSISTENT']

traded_watchlist = []

while True:
    for stock_name in watchlist:
        try:
            chart = tsl.get_intraday_data(stock_name, 'NSE', 15)
            if not isinstance(chart, pd.DataFrame) or chart.empty:
                print(f"Skipping {stock_name} due to missing data (DH-907 Error)")
                continue
        except Exception as e:
            print(f"Skipping {stock_name} due to error: {e}")
            continue
      
        # Calculate RSI
        chart['rsi'] = talib.RSI(chart['close'], timeperiod=14)

        # Calculate ATR
        chart['ATR'] = talib.ATR(chart['high'], chart['low'], chart['close'], timeperiod=14)

        # Ensure sufficient data
        if len(chart) < 4:
            continue

        bc = chart.iloc[-2]  # Breakout candle
        ic = chart.iloc[-3]  # Inside candle
        ba_c = chart.iloc[-4]  # Base candle

        uptrend = bc['rsi'] > 50
        downtrend = bc['rsi'] < 49
        inside_candle_formed = (ba_c['high'] > ic['high']) and (ba_c['low'] < ic['low'])
        upper_side_breakout = bc['high'] > ba_c['high']
        down_side_breakout = bc['low'] < ba_c['low']
        no_repeat_order = stock_name not in traded_watchlist
        max_order_limit = len(traded_watchlist) <= max_trades

        # Get latest ATR value
        atr_value = chart.iloc[-1]['ATR']

        if uptrend and inside_candle_formed and upper_side_breakout and no_repeat_order and max_order_limit:
            entry_price = bc['close']
            trigger_gap = 0.05 * entry_price
            stop_loss = entry_price - (atr_multiplier_sl * atr_value)
            target_profit = entry_price + (atr_multiplier_tp * atr_value)
            qty = int(per_trade_margin / entry_price)

            print(f"{stock_name} BUY at {entry_price}, TP: {target_profit}, SL: {stop_loss}, Time: {datetime.datetime.now()}")
            
            # buy_entry_orderid = tsl.order_placement(stock_name, 'NSE', qty, take_profit, stop_loss, 'MARKET', 'BUY', 'MIS')
            buy_entry_orderid = tsl.order_placement(tradingsymbol=stock_name,exchange='NSE',quantity=qty,transaction_type="BUY",
                                    price=entry_price, trigger_price=entry_price-trigger_gap,order_type="LIMIT",trade_type="BO",
                                    after_market_order=False,validity="DAY",bo_profit_value=target_profit,bo_stop_loss_Value=stop_loss
                                    )
            traded_watchlist.append(stock_name)

        if downtrend and inside_candle_formed and down_side_breakout and no_repeat_order and max_order_limit:
            entry_price = bc['close']
            trigger_gap = 0.05 * entry_price
            stop_loss = entry_price + (atr_multiplier_sl * atr_value)
            target_profit = entry_price - (atr_multiplier_tp * atr_value)
            qty = int(per_trade_margin / entry_price)

            print(f"{stock_name} SELL at {entry_price}, TP: {target_profit}, SL: {stop_loss}, Time: {datetime.datetime.now()}")

            # sell_entry_orderid = tsl.order_placement(stock_name, 'NSE', qty, take_profit, stop_loss, 'MARKET', 'SELL', 'MIS')
            sell_entry_orderid = tsl.order_placement(tradingsymbol=stock_name,exchange='NSE',quantity=qty,price=entry_price,
                                    trigger_price=entry_price+trigger_gap,transaction_type="SELL",order_type="LIMIT",trade_type="BO",
                                    validity="DAY",amo_time=None,bo_profit_value=target_profit,bo_stop_loss_Value=stop_loss
                                    )
            traded_watchlist.append(stock_name)
        print("scanned", stock_name)