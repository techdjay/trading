tickers = [*si.tickers_nasdaq(), *si.tickers_other()]

with open('tickers.csv', 'w') as f:
    print(*tickers, sep='\n', file=f)