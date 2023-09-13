import flask
from flask import request, jsonify, abort
import yahoofinanceapi.ticker as yf
from yahoofinanceapi.ticker import Ticker

tickerStrings = ['SBIN.NS', 'PNB.NS']
start = '2021-07-30'
end = '2021-07-30'

for symbol in tickerStrings:
    data = Ticker(symbol, start_day='start', end_day= 'end', interval='5m' )
    #data['ticker'] = ticker# add this column becasue the dataframe doesn't contain a column with the ticker
    #df[Datetime]= Datetime
    #data.to_csv(f'ticker_{ticker}.csv')  # ticker_AAPL.csv for example
    print(data)

#.format(symbol, symbol, start_day, end_day, interval, includePrePost, self.crumbs)