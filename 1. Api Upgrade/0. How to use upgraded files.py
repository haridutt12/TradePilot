# pip install --upgrade dhanhq

import pdb
import time
import datetime
import traceback
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
from pprint import pprint
import talib

# ---------------for dhan login ----------------

client_code = "1102790337"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMxNDc5MTg1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMjc5MDMzNyJ9.cJFmav3LOCQqz9Tp-KRJFPEYR-1Ds3G9YiZqXxcTfnQ3Nqgi4JJNd-y4XRbhfQD5RFAVLooTfZzpUGGstaLYLw"

tsl = Tradehull(client_code,token_id)

ltp_data = tsl.get_ltp_data(names = ['BANKNIFTY', 'NIFTY' ,'CRUDEOIL', 'RELIANCE', 'NIFTY 07 NOV 24000 CALL', 'NIFTY 07 NOV 24000 PUT', 'CRUDEOIL 15 NOV 5950 CALL', 'CRUDEOIL 15 NOV 5950 PUT'])

data = tsl.get_historical_data(tradingsymbol = 'BANKNIFTY',exchange = 'INDEX',timeframe="DAY")
data = tsl.get_historical_data(tradingsymbol = 'ACC'     ,exchange = 'NSE'  ,timeframe="15")


options_chart = tsl.get_historical_data(tradingsymbol = 'NIFTY 07 NOV 24000 CALL'     ,exchange = 'NFO'  ,timeframe="15")
options_chart['ema_30'] = talib.EMA(options_chart['close'], timeperiod=30)

data = tsl.get_historical_data(tradingsymbol = 'CRUDEOIL NOV FUT' ,exchange = 'MCX'  ,timeframe="15")
data = tsl.get_historical_data(tradingsymbol = 'CRUDEOIL 15 NOV 5950 CALL'     ,exchange = 'MCX'  ,timeframe="15")


order_details = tsl.get_order_detail(orderid=102241104416927)
order_status  = tsl.get_order_status(orderid=102241104416927)
order_price   = tsl.get_executed_price(orderid=102241104416927)
order_time    = tsl.get_exchange_time(orderid=102241104416927)


positions = tsl.get_positions()
orderbook = tsl.get_orderbook()
tradebook = tsl.get_trade_book()
holdings = tsl.get_holdings()


ce_strike, pe_strike, strike = tsl.ATM_Strike_Selection(Underlying ='CRUDEOIL',Expiry ='15-11-2024')
ce_strike, pe_strike, ce_OTM_price, pe_OTM_price = tsl.OTM_Strike_Selection(Underlying ='CRUDEOIL',Expiry ='15-11-2024',OTM_count=5)
ce_strike, pe_strike, ce_ITM_price, pe_ITM_price = tsl.ITM_Strike_Selection(Underlying = 'CRUDEOIL',Expiry = '15-11-2024',ITM_count=1)


