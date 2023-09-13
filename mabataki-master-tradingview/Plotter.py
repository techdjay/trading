import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data, wb
from datetime import timedelta



def getValue(path):
        df = pd.read_csv(path+".csv", index_col=0)
        high_9 = df['high'].rolling(window= 9).max()
        low_9 = df['low'].rolling(window= 9).min()
        df['tenkan_sen'] = (high_9 + low_9) /2
        high_26 = df['high'].rolling(window= 26).max()
        low_26 = df['low'].rolling(window= 26).min()
        df['kijun_sen'] = (high_26 + low_26) /2
        # this is to extend the 'df' in future for 26 days
        # the 'df' here is numerical indexed df
        last_index = df.iloc[-1:].index[0]
        last_date = pd.to_datetime(df['date'].iloc[-1]).date()
        for i in range(26):
            df.loc[last_index+1 +i, 'date'] = last_date + timedelta(days=i)

        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        high_52 = df['high'].rolling(window= 52).max()
        low_52 = df['low'].rolling(window= 52).min()
        df['senkou_span_b'] = ((high_52 + low_52) /2).shift(26)

        # most charting softwares dont plot this line
        df['chikou_span'] = df['close'].shift(-22) #sometimes -26 

        tmp = df[['date','close','senkou_span_a','senkou_span_b','kijun_sen','tenkan_sen']].tail(300)
        tmp.set_index('date')

        #a1 = tmp.plot(figsize=(15,10))
        #a1.fill_between(tmp.index, tmp.senkou_span_a, tmp.senkou_span_b)

        #plt.show()
        df.drop(df.tail(26).index, inplace = True)

        current = df.tail(1)

        global close_value
        global senkou_span_a
        global senkou_span_b

        close_value = current['close'].values[0]
        senkou_span_a = current['senkou_span_a'].values[0]
        senkou_span_b = current['senkou_span_b'].values[0]


        print(close_value)
        print(senkou_span_a)
        print(senkou_span_b)


        if close_value > senkou_span_a and close_value > senkou_span_b:
            return int(1)
        
        if senkou_span_a  > close_value and senkou_span_b > close_value:
            return int(-1)
        if senkou_span_a > close_value and close_value > senkou_span_b:
            return int(0)
        
        if senkou_span_b > close_value and close_value > senkou_span_a:
            return int(2)

def getClose():
    return close_value

def getSenkouA():
    return float(senkou_span_a)

def getSenkouB():
    return float(senkou_span_b)


