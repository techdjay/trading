#Testing for Zerodha EOD Data, Trying to multithread the process
import _thread as thread
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from datetime import date
import datetime
import threading
from win32com.client import Dispatch
import win32com.client as wcl
import os

ab = wcl.Dispatch("Broker.Application")
AmiBroker = Dispatch("Broker.Application")
AmiBroker.visible = True
AmiBroker.LoadDatabase('C:/AmiFeeds/Amibroker/AFData')

filePath = 'C:\ZerodhaHistoricalData\eoddata.csv';
# As file at filePath is deleted now, so we should check if file exists or not not before deleting them
if os.path.exists(filePath):
    os.remove(filePath)
else:
    print("Can not delete the file as it doesn't exists")

start_date = date(2022, 8, 1)  # yyyy-mm-dd format
end_date = date(2023, 9, 14)  # yyyy-mm-dd format
day = 30 #day=30 max  min = for current day 1
dy = 30 #dy=31 max min= for current day 1
userid = 'ZG7393'
timeframe = 'day'  # day , minute, 5minute, 3hour
#ciqrandom = '161746886774'

auth_token = 'enctoken uf+hEsxRAxAiQlf5vbOwoD+qsGrV6NjXyCf+u1N1Tq+YoMANHicuq3qqS9IPVJNdM2Amze5qzQAxlnJ/ms/Nna++cH8FG4c8FwrPYwXHnrWWvi/PZ5+Nfg=='
headers = {'authorization': auth_token,
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            "Authority": "kite.zerodha.com",
           "method": 'method',
           "path": 'path',
           "scheme": "https",
           "Accept":'*/*',
           "Accept-Encoding":"utf-8",
           "Accept-Language":"en-US,en;q=0.5",
           "Connection":"keep-alive",
           "Cookie": 'cookie',"Host":"kite.zerodha.com","Referer":'referer',"sec-fetch-dest":"empty","sec-fetch-mode": "cors","sec-fetch-site": "same-origin"}

#start = time.time()
#intraday data
#token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\zerodha_ins_for_intra_ami.xlsx')
#token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\nifty50listzrodha.xlsx')
#eod data
token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\zerodha_ins_for_eod_ami.xlsx')
#indices
#token_df = pd.read_excel(r'C:\Users\Jay\Desktop\Trading\zd_instrument\Zerodha_Indices.xlsx')

def dataa(self):
    for i in range(0, len(token_df)):
        #start1 = time.time()
        token = token_df.loc[i]['TOKEN']
        columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'V', 'OI']
        final_df = pd.DataFrame(columns=columns)
        from_date = start_date

        while from_date < end_date:
            to_date = from_date + timedelta(days= (day))  #days=30

            url = f'https://kite.zerodha.com/oms/instruments/historical/{token}/{timeframe}?user_id={userid}&oi=1&from={from_date}&to={to_date}'
            try:
                resJson = requests.get(url, headers=headers).json()
                if 'data' in resJson and 'candles' in resJson['data']:
                    candelinfo = resJson['data']['candles']
                    # Process candelinfo here
                else:
                    print("Invalid response format")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")

            df = pd.DataFrame(candelinfo, columns=columns)

            final_df = final_df.append(df, ignore_index=True)
            from_date = from_date + timedelta(days= (dy)) #days=31

        # final_df['timestamp'] = pd.to_datetime(final_df['timestamp'],format = '%Y-%m-%dT')
        # final_df['date'] = pd.to_datetime(final_df['timestamp']).dt.date
        # final_df['time'] = pd.to_datetime(final_df['timestamp']).dt.strftime('%H:%M:%S')

        # this line converts the string object in Timestamp object
        final_df['timestamp'] = [datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z') for d in final_df['timestamp']]
        # extracting date from timestamp
        final_df['date'] = [datetime.datetime.date(d) for d in final_df['timestamp']]
        # extracting time from timestamp
        final_df['time'] = [datetime.datetime.time(d) for d in final_df['timestamp']]
        final_df['ticker'] = token_df.loc[i]['SYMBOL']
        final_df.drop('timestamp', axis=1, inplace=True)
        final_df = final_df[['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'V', 'OI', 'time']]
        #filename = str(token_df.loc[i]['SYMBOL']) +'eod.csv'
        final_df.to_csv('C:/ZerodhaHistoricalData/eoddata.txt', mode='w', header=False, index=False)
        #final_df.to_csv('C:/ZerodhaHistoricalData/eoddata.csv', mode='a', header=False, index=False)
        print(final_df)
        path = 'C:/ZerodhaHistoricalData/eoddata.txt'
        #ab.Import(0, 'C:\\Users\\Jay\\Desktop\\Trading\\stock-market-scraper-master-yahoo\\test_c.txt',
        #          "autouploaddata.format")
        ab.Import(0, path, "Zerodhaieoddata.format")
        print(token_df.loc[i]['SYMBOL'],'Data imported successfully')


        #os.remove(filePath)
       # print(time.time() - start1)
#AmiBroker.RefreshAll()
#AmiBroker.SaveDatabase()
print("Saving Data!")
#x1 = threading.Thread(target = dataa('self'))
#x1.start()
#time.sleep(.2)
#print('Done')
#time.sleep(50)
if __name__ == '__main__':
  #  print('Saving data to Amibroker')
  #  dataa()
  #  save_toami()
    # creating thread
    t1 = threading.Thread(target=dataa('self'))


    # starting thread 1
    t1.start()
    # starting thread 2

    print(threading.activeCount())
    # wait until thread 1 is completely executed
    #t1.join()
    # wait until thread 2 is completely executed
    #t2.join()

    # both threads completely executed
    #print("Done!")

