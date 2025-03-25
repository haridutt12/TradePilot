import pdb
import time
import datetime
import traceback
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
from pprint import pprint
import talib


client_code = "1102790337"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMxNDc5MTg1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMjc5MDMzNyJ9.cJFmav3LOCQqz9Tp-KRJFPEYR-1Ds3G9YiZqXxcTfnQ3Nqgi4JJNd-y4XRbhfQD5RFAVLooTfZzpUGGstaLYLw"
tsl = Tradehull(client_code,token_id)



data_day = tsl.get_historical_data(tradingsymbol = 'BANKNIFTY',exchange = 'INDEX',timeframe="DAY")
data_5 = tsl.get_historical_data(tradingsymbol = 'BANKNIFTY',exchange = 'INDEX',timeframe="5")


options_data = tsl.get_historical_data(tradingsymbol = 'NIFTY 07 NOV 24000 CALL',exchange = 'NFO',timeframe="5")
options_data['ema30'] = talib.EMA(options_data['close'], timeperiod=30)




pdb.set_trace()




order_details = tsl.get_order_detail(orderid=102241105310027)
order_status  = tsl.get_order_status(orderid=102241105310027)
order_price   = tsl.get_executed_price(orderid=102241105310027)
order_time    = tsl.get_exchange_time(orderid=102241105310027)














