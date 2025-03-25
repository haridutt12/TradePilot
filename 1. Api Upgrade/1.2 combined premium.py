# pip install --upgrade dhanhq

import pdb
import time
import datetime
import traceback
from Dhan_Tradehull_V2 import Tradehull
import pandas as pd
from pprint import pprint
import talib
import time


# ---------------for dhan login ----------------
client_code = "1102790337"
token_id    = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMxNDc5MTg1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMjc5MDMzNyJ9.cJFmav3LOCQqz9Tp-KRJFPEYR-1Ds3G9YiZqXxcTfnQ3Nqgi4JJNd-y4XRbhfQD5RFAVLooTfZzpUGGstaLYLw"

tsl = Tradehull(client_code,token_id)





call_list = ["NIFTY 07 NOV 24000 CALL", "NIFTY 07 NOV 24000 PUT"]





while True:
	current_time = datetime.datetime.now()
	ltp_data = tsl.get_ltp_data(names = call_list)
	ce_ltp = ltp_data['NIFTY 07 NOV 24000 CALL']
	pe_ltp = ltp_data['NIFTY 07 NOV 24000 PUT'] 

	atm_combined_premium = ce_ltp + pe_ltp
	print(current_time, atm_combined_premium)
	time.sleep(0.5)



