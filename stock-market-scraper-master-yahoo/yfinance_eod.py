import yfinance as yf
import datetime as dt

tickerStrings=['TATASTEEL.NS']
for i in range(len(tickerStrings)):
    data = yf.download(tickerStrings[i], start="2021-08-16", interval="1m", threads=True)
    #symbol = tickerStrings[i].split('.')[0]  # remove .NS
    #data['ticker'] = symbol
print(data)