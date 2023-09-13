import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from datetime import date
import datetime
import queue
from threading import Thread
#import    urllib2
from threading import  Thread
from time import sleep
import urllib3
import urllib.request

import os
filePath = 'C:\ZerodhaHistoricalData\eoddata.csv';
# As file at filePath is deleted now, so we should check if file exists or not not before deleting them
if os.path.exists(filePath):
    os.remove(filePath)
else:
    print("Can not delete the file as it doesn't exists")

start_date = date(2021,8,11)   #yyyy-mm-dd format
end_date =  date(2021,8,13)     #yyyy-mm-dd format

userid = 'ZG7393'
timeframe= 'minute'
ciqrandom = '161746886774'

auth_token = 'enctoken oLERB6P6yD+ueN/aBEamq/x1uAtrmD4FzLjIZE9Vv+9oOxZOxhxUXFOKoOY9eJ8+vSIUJ+66DWaxmOM52GpTDTxdEMlUhEI6znGvoy8tUR0YDAh0rUs31Q=='
headers = {'Authorization': auth_token}


start = time.time()
token_df = pd.read_excel(r'C:\\token_symbol.xlsx')
for i in range(0,len(token_df)):
        start1 = time.time()
        token = token_df.loc[i]['TOKEN']
        columns = ['timestamp','Open','High','Low','Close','V','OI']
        final_df = pd.DataFrame(columns=columns)
        from_date = start_date

        while from_date < end_date :

            to_date =  from_date + timedelta(days=30)



            url = f'https://kite.zerodha.com/oms/instruments/historical/{token}/{timeframe}?user_id={userid}&oi=1&from={from_date}&to={to_date}'
            resJson = requests.get(url, headers=headers).json()
            candelinfo = resJson['data']['candles']
            df= pd.DataFrame(candelinfo, columns=columns)

            final_df = final_df.append(df,ignore_index=True)
            from_date = from_date + timedelta(days=31)

       # final_df['timestamp'] = pd.to_datetime(final_df['timestamp'],format = '%Y-%m-%dT')
       # final_df['date'] = pd.to_datetime(final_df['timestamp']).dt.date
        #final_df['time'] = pd.to_datetime(final_df['timestamp']).dt.strftime('%H:%M:%S')


        # this line converts the string object in Timestamp object
        final_df['timestamp'] = [datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z') for d in final_df['timestamp']]

        # extracting date from timestamp
        final_df['date'] = [datetime.datetime.date(d) for d in final_df['timestamp']]

        # extracting time from timestamp
        final_df['time'] = [datetime.datetime.time(d) for d in final_df['timestamp']]

        final_df['ticker'] = token_df.loc[i]['SYMBOL']
        final_df.drop('timestamp',axis = 1,inplace = True)
        final_df = final_df[['ticker','date','Open','High','Low','Close','V','OI','time']]

        #filename = str(token_df.loc[i]['SYMBOL']) +'eod.csv'
        final_df.to_csv('C:/ZerodhaHistoricalData/eoddata.csv', mode='a', header =False,index = False )
        
        print(time.time() - start1)
        print(final_df)
        
 #print(time.time() - start)      
from win32com.client import Dispatch
import win32com.client as wcl
from shutil import copyfile
import os
import time as tm
ab = wcl.Dispatch("Broker.Application")
AmiBroker = Dispatch("Broker.Application")
AmiBroker.visible=True
AmiBroker.LoadDatabase(AFData)
AmiBroker.RefreshAll()
AmiBroker.SaveDatabase()

def save_data():
    path = 'C:/ZerodhaHistoricalData/eoddata.csv'
    #copyfile('C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test.txt', 'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt')
   # ab.Import(0,'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt', "autouploaddata.format");
    #ab.RefreshAll();
    AmiBroker.Import(0, path, "autouploaddata.format")
    AmiBroker.RefreshAll()

    tm.sleep(0.100)
if __name__ == '__main__':
	save_data()
