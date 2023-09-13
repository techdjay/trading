#from yflive import QuoteStreamer
import yliveticker
import datetime
import pandas as pd
import time as tm
import sys
import os
#import copydata
import pandas as pd
from shutil import copyfile
def on_new_msg(ws, data):
    #print(data)
    #global row_no   #marked already written data to global to not replace
    sys.stdout = open("yflivequotestreamer.txt", "w")
    sym = data['id']
    symbol = sym.split('.')[0]  # remove .NS
    ltp = data['price']
    time_date = data['timestamp']  #original time stamp
    dt = datetime.datetime.fromtimestamp(int(time_date) / 1000)  #converted 13digit to 10Dgit timestamp
    time = dt.strftime("%Y-%m-%d %H:%M:%S")   #Converted in time Date formate
    #time =  dt.strftime("%X") #change date time to time only
    #volume = data['dayVolume']
    #df = symbol, ltp, time
    print(symbol, ltp, time)
    #dataframe =pd.DataFrame(data=df)
   # dataframe.to_csv("yflivequotestreamer.txt")
    #sys.stdout.close()
    #tm.sleep(1)
    #copydata.save_data()
    #print("Data saved")
yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=["ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "HDFC.NS", "ICICIBANK.NS", "ITC.NS", "IOC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHREECEM.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"])
#if __name__ == '__main__':
#    on_new_msg()

