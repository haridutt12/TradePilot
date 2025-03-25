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




call_list = ["NIFTY 07 NOV 23500 CALL", "NIFTY 07 NOV 23550 CALL", "NIFTY 07 NOV 23600 CALL", "NIFTY 07 NOV 23650 CALL", "NIFTY 07 NOV 23700 CALL", "NIFTY 07 NOV 23750 CALL", "NIFTY 07 NOV 23800 CALL", "NIFTY 07 NOV 23850 CALL", "NIFTY 07 NOV 23900 CALL", "NIFTY 07 NOV 23950 CALL", "NIFTY 07 NOV 24000 CALL", "NIFTY 07 NOV 24050 CALL", "NIFTY 07 NOV 24100 CALL", "NIFTY 07 NOV 24150 CALL", "NIFTY 07 NOV 24200 CALL", "NIFTY 07 NOV 24250 CALL", "NIFTY 07 NOV 24300 CALL", "NIFTY 07 NOV 24350 CALL", "NIFTY 07 NOV 24400 CALL", "NIFTY 07 NOV 24450 CALL", "NIFTY 07 NOV 24500 CALL"]


ltp_data = tsl.get_ltp_data(names = call_list)

for script_name,ltp in ltp_data.items():

	if ltp < 50:
		print(f"for {script_name} the ltp is {ltp}")
		break







