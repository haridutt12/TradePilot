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



pdb.set_trace()

buy_entry_orderid = tsl.order_placement(stock_name,'NSE', 1, 0, 0, 'MARKET', 'BUY', 'MIS')



order_details = tsl.get_order_detail(orderid=buy_entry_orderid)


# double check if order is completd
order_status  = tsl.get_order_status(orderid=buy_entry_orderid)
if order_status == "TRADED":
	print("I have double checked Order Completed")




order_price   = tsl.get_executed_price(orderid=buy_entry_orderid)
sl_price      = round((order_price*0.98),1)



order_time    = tsl.get_exchange_time(orderid=buy_entry_orderid)
order_sent_time  = datetime.datetime.strptime(order_time, '%Y-%m-%d %H:%M:%S')
time_spent = ((datetime.datetime.now() - order_sent_time).total_seconds()/60)

if (time_spent > 30) and (order_status != 'TRADED'):
	tsl.cancel_order(OrderID)













ce_strike, pe_strike, strike = tsl.ATM_Strike_Selection(Underlying ='CRUDEOIL',Expiry ='15-11-2024')
ce_strike, pe_strike, ce_OTM_price, pe_OTM_price = tsl.OTM_Strike_Selection(Underlying ='CRUDEOIL',Expiry ='15-11-2024',OTM_count=5)
ce_strike, pe_strike, ce_ITM_price, pe_ITM_price = tsl.ITM_Strike_Selection(Underlying = 'CRUDEOIL',Expiry = '15-11-2024',ITM_count=1)


