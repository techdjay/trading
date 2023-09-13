import pandas as pd
from datetime import datetime
import requests

def isUrlValid(url):
    try:
        requests.get(url, timeout = 5)
    except Exception as e:
        return False
    else:
        return True
    

#dateformat MM/DD/YYYY
#enter start and end date as per your requirement
dt = pd.date_range(start="10/27/2020", end='10/28/2020', freq='B') 
for tday in dt:
    try:
        dmyformat = datetime.strftime(tday,'%d%m%Y')
        dMMyFormatUpperCase = datetime.strftime(tday,'%d%b%Y').upper()
        filenamedate = datetime.strftime(tday,'%m%d%Y').upper()
        monthUppercase = datetime.strftime(tday,'%b').upper()
        year = datetime.strftime(tday,'%Y')
        
        url_dlvry = 'https://archives.nseindia.com/archives/equities/mto/MTO_'+ dmyformat +'.DAT'
        if not isUrlValid(url_dlvry):
            continue
        print(url_dlvry)
        data1 = pd.read_csv(url_dlvry,skiprows=3) 
        data1 = data1[ data1['Name of Security'] == 'EQ']
        data1 = data1.rename(columns={"Sr No": "SYMBOL"})
         
        
        url_bhav = 'https://archives.nseindia.com/content/historical/EQUITIES/'+ year + '/' + monthUppercase +'/cm' +dMMyFormatUpperCase+'bhav.csv.zip'
        print(url_bhav)
        data2 = pd.read_csv(url_bhav) 
        data2 = data2[ data2['SERIES'] == 'EQ']

        result = pd.merge(data2, data1, on='SYMBOL')
        result = result[['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE','TOTTRDQTY','Deliverable Quantity(gross across client level)','TOTALTRADES',]]

        filename = filenamedate + '_NSE.txt'
        #change download path as per your system
        result.to_csv('E:\\Trading Stuff\\bhavcopy\\fno\\' + filename, header =False,index = False )
        print("Data Successfully write for " + dMMyFormatUpperCase )
    except Exception as e:
        print("Oops!  Error in " , e  )
print("Done!")