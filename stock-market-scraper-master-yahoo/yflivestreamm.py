import yliveticker
import pandas as pd
import psycopg2
from io import StringIO
import xlwings as xw

import datetime
import win32com.client as wcl
import time as td
#Writing data in Excel
wb = xw.Book('Tick Data.xlsx')
sht =wb.sheets('Sheet1')
row_no = 2

def on_new_msg(ws, data):
  #  print(data)
    global row_no   #marked already written data to global to not replace
    symbol = data['id']
    ltp = data['price']
    time_date = data['timestamp']  #original time stamp
    dt = datetime.datetime.fromtimestamp(int(time_date) / 1000)  #converted 13digit to 10Dgit timestamp
    time = dt.strftime("%Y-%m-%d %H:%M:%S")   #Converted in time Date formate
    #time =  dt.strftime("%X") #change date time to time only
    volume = data['dayVolume']
    print(symbol, ltp, time, volume)
    sht.range('A' + str(row_no)).value = symbol
    sht.range('B' + str(row_no)).value = ltp
    sht.range('C' + str(row_no)).value = time
    sht.range('D' + str(row_no)).value = volume
    row_no = row_no + 1
    td.sleep(1)
yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=["RELIANCE.NS", "BTC-USD"
                                                            ])

#{'id': 'BTC-USD', 'exchange': 'CCC', 'quoteType': 41, 'price': 43612.375, 'timestamp': 1628332382000,
# 'marketHours': 1, 'changePercent': 7.820406913757324, 'dayVolume': 40983056384, 'change': 3163.28125,
# 'priceHint': 2}


#data1 = pd.DataFrame(on_new_msg)
# dataframe type to type str IO buffer
#output = StringIO()
#data1.to_csv(output, sep='\t', index=True, header=False)
#output1 = output.getvalue()
# print(data1)
#conn = psycopg2.connect(host='localhost', user='postgres', password='postgres', database='yahoo')
#cur = conn.cursor()
#cur.copy_from(StringIO(output1), 'stockdatalive')
#conn.commit()

#print('done')
