import cryptocompare as cryp

import datetime





# data = cryp.get_coin_list(format=False)
# print(data.keys())

# print(cryp.get_price("BTC","USDT"))
# data = cryp.get_historical_price_day('BTC', 'USDT', limit=24, exchange='CCCAGG', toTs=datetime.datetime(2019,6,6))
# print(data)

1440
# cryp.get_historical_price_hour()
DATAM = cryp.get_historical_price_minute('BTC', currency='USDT',exchange="CCCAGG", limit=10)
for i in DATAM:
    time = datetime.datetime.fromtimestamp(i["time"])
    i.update({"time":time})
    print(i)