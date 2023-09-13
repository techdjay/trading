import streamlit as st
import pandas as pd
import numpy as np
import mplfinance as mpf
import datetime
import time
import pandas_ta as ta
from IPython.display import clear_output
import math
import altair as alt
import base64
from io import BytesIO
from tvDatafeed.main import TvDatafeed,Interval
from PIL import Image
from pathlib import Path


tv=TvDatafeed(chromedriver_path=None)




#st.beta_set_page_config(page_title='Velocity Trading')
def timePeriodFormatter(timePeriod):
    if (timePeriod=="1m"):
        resolution=Interval.in_1_minute
    elif (timePeriod=="3m"):
        resolution=Interval.in_3_minute
    elif (timePeriod=="5m"):
        resolution=Interval.in_5_minute
    elif (timePeriod=="15m"):
        resolution=Interval.in_15_minute
    elif (timePeriod=="30m"):
        resolution=Interval.in_30_minute
    elif (timePeriod=="45m"):
        resolution=Interval.in_45_minute
    elif (timePeriod=="1H"):
        resolution=Interval.in_1_hour
    elif (timePeriod=="2H"):
        resolution=Interval.in_2_hour
    elif (timePeriod=="3H"):
        resolution=Interval.in_3_hour
    elif (timePeriod=="4H"):
        resolution=Interval.in_4_hour
    elif (timePeriod=="1D"):
        resolution=Interval.in_daily
    elif (timePeriod=="1W"):
        resolution=Interval.in_weekly
    elif (timePeriod=="1M"):
        resolution=Interval.in_monthly
    else:
         resolution=Interval.in_5_minute
    return resolution


def signal(data,mag=100):
    data['signalLong']=np.nan
    data['signalShort']=np.nan
    cond1=data['reversal']==1
    cond2=data['pos']==1
    data.loc[cond1&cond2,'signalLong']=data['low']*0.9995
    data.loc[cond1& ( ~cond2),'signalShort']=data['high']*1.0005
    sigLong = data['signalLong'].tolist()
    sigShort = data['signalShort'].tolist()
    addPlot1= mpf.make_addplot(sigLong[-mag:],type='scatter',markersize=50,marker='^')
    addPlot2= mpf.make_addplot(sigShort[-mag:],type='scatter',markersize=50,marker='v')
    return addPlot1,addPlot2

def currTrade(data, commission,mult=1):
    data.reset_index(inplace=True,drop=False)
    curr=data.iloc[-1]
    rev=data[data['reversal']==1].iloc[-1]
    currPosition=curr.pos
    entry=rev.open
    price=curr.close
    if currPosition==1:
        net=price-entry
        position="Buy"
    else:
        net=entry-price
        position="Sell"
    net=(round(net,2)-(entry*commission/200))*mult
    row=data.iloc[4]
    data.set_index("datetime",drop=True,inplace=True)
    data=[row.symbol,position,rev.datetime.date(),rev.datetime.time(),curr.datetime.date(),curr.datetime.time(),entry,price,net,(net/entry)*100]
    tradeOutput=["Symbol","Signal",'Entry Date','Entry Time','Current Date','Current Time',"Entry Price",'Current Price',"Net Points Captured","ROI(%)"]
    df = pd.DataFrame([data], columns = tradeOutput)
    df.index += 1 
    df=df.round(2).astype(object)
    return df

def ma(data, length, type, mag=100):
    if(type=='ema'):
        data['ma']=ta.ema(data['close'],length=length,fillna=0)
    else:
        data['ma']=ta.wma(data['close'],length=length,fillna=0)
    cond1=(data['close'].shift(1))>=(data['ma'].shift(1))
    cond2=(data['close'].shift(1))<(data['ma'].shift(1))
    data.loc[cond1,'pos']=1
    data.loc[cond2,'pos']=-1
    data['reversal']=0
    data.loc[data['pos'].shift(1)!=data['pos'],'reversal']=1
    addPlot1,addPlot2=signal(data,mag)
    addPlot3 = mpf.make_addplot(data['ma'].tail(mag))
    addPlot=[addPlot1,addPlot2,addPlot3]
    data=data[data['ma'].notna()]
    return data,addPlot

def ftsma(data, lenFast, lenMid, lenSlow, mag=100):
    data['slow']=ta.ema(data['close'],length=lenSlow,fillna=0)
    data['mid']=ta.ema(data['close'],length=lenMid,fillna=0)
    data['fast']=ta.ema(data['close'],length=lenFast,fillna=0)

    cond1=(data['fast'].shift(1))>(data['mid'].shift(1))
    cond2=(data['close'].shift(1))>(data['slow'].shift(1))
    data.loc[cond1 & cond2 ,'pos']=1
    data.loc[~cond1 & ~cond2,'pos']=-1
    data=data.ffill()
    data['reversal']=0
    data.loc[data['pos'].shift(1)!=data['pos'],'reversal']=1
    
    addPlot1,addPlot2=signal(data,mag)
    addPlot3 = mpf.make_addplot(data['fast'].tail(mag))
    addPlot4 = mpf.make_addplot(data['mid'].tail(mag))
    addPlot5 = mpf.make_addplot(data['slow'].tail(mag))
    addPlot=[addPlot1,addPlot2,addPlot3,addPlot4,addPlot5]
    return data,addPlot

def supertrend(data, atrlen, superMult,mag=100):
    df=ta.supertrend(data['high'],data['low'],data['close'],atrlen,superMult)
    data['pos']=df.iloc[:,1]
    data.pos=data.pos.shift(1)
    data['reversal']=0
    data.loc[data['pos'].shift(1)!=data['pos'],'reversal']=1
    addPlot1,addPlot2=signal(data,mag)
    addPlot=[addPlot1,addPlot2]
    return data,addPlot

def psar(data, psarAf, psarMaxAf,mag=100):
    df=ta.psar(data['high'],data['low'],data['close'],psarAf,psarMaxAf)
    data['pos']=df.iloc[:,0]
    data=data.fillna(-1)
    data.loc[data['pos']!=-1.0,'pos']=1
    data.pos=data.pos.shift(1)
    data['reversal']=0
    data.loc[data['pos'].shift(1)!=data['pos'],'reversal']=1
    addPlot1,addPlot2=signal(data,mag)
    addPlot=[addPlot1,addPlot2]
    return data,addPlot

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="download.xlsx">Download list of trades as an excel file</a>' # decode b'abc' => abc


def backtest(data,start=datetime.date.today()-datetime.timedelta(days=500),end=datetime.date.today(),comm=0.0,flag=0,mult=1,buyHold=0):
    trades=data
    trades=trades[trades['reversal']==1]
    if trades.empty & flag==1:
        placeholder1.write("No trades executed during this time interval")
        return 0
    trades.reset_index(inplace=True,drop=False)

    trades['Entry Time']=trades['datetime'].shift(1).dt.time
    trades['Exit Time']=trades['datetime'].dt.time
    trades['Entry Date']=trades['datetime'].shift(1).dt.date
    trades['Exit Date']=trades['datetime'].dt.date
    trades['Signal']='Sell'
    trades.loc[trades['pos'].shift(1)==1.0,'Signal']='Buy' 
    trades['Entry']=trades['open'].shift(1)
    trades['Exit']=trades['open']
    trades['Net(After Commissions)']=(trades['open']-trades['open'].shift(1))*mult
    trades.loc[trades['Signal']=='Sell','Net(After Commissions)']=-1.0*trades['Net(After Commissions)']
    trades['Net(After Commissions)']=trades['Net(After Commissions)']-(trades['open']*comm*mult/100)
    trades['Total PnL(After Commissions)']=trades['Net(After Commissions)'].cumsum(axis=0)
    trades['Symbol']=trades['symbol']
    trades['Price']=trades['open']
    trades['ROI(%)']=(trades['Net(After Commissions)']/trades['Entry'])*100/mult
    startVal=trades['open'].iloc[0]
    trades=trades[['Symbol','Entry Date','Entry Time','Exit Date','Exit Time','Signal','Entry','Exit','Net(After Commissions)','Total PnL(After Commissions)','Price','ROI(%)','datetime']]
    totalNet=trades.iloc[-1]['Total PnL(After Commissions)']
    totalComm=(comm/100)*mult*trades['Entry'].sum()
    netLong=trades.loc[trades['Signal']=='Buy','Net(After Commissions)'].sum()
    netShort=trades.loc[trades['Signal']=='Sell','Net(After Commissions)'].sum()
    trades.reset_index(inplace=True,drop=True)
    trades.dropna(inplace=True)
    rows=[netLong,netShort,len(trades.index),totalComm,totalNet,(netLong/(startVal*mult))*100,(totalNet/(startVal*mult))*100,buyHold*mult,(buyHold/startVal)*100]
    tradeOutput=["Net Buy(After Commissions)","Net Sell(After Commissions)","Trades","Total Commissions","Net PnL(After Commissions)","Buy ROI(%)","Total Buy/Sell ROI(%)","Buy & Hold PnL","Buy Hold ROI(%)"]
    df = pd.DataFrame([rows], columns = tradeOutput)
    trades['Net']=trades['Net(After Commissions)']
    trades['Net Points Captured']=trades['Net(After Commissions)']
    trades['Net Points Captured(After Commissions)']=trades['Net(After Commissions)']
    trades['Buy Only PnL(After Commissions)']=trades[trades['Signal']=='Buy'].Net.cumsum()
    trades=trades.ffill()
    if flag==1:
        
        trades.set_index('datetime',inplace=True)
        placeholder1.line_chart(trades['Price'], use_container_width=True)
        placeholder2.line_chart(trades['Buy Only PnL(After Commissions)'], use_container_width=True)
        placeholder3.line_chart(trades['Total PnL(After Commissions)'], use_container_width=True)
        df.index += 1 
        df=df.round(2).astype(object)
        placeholder4.subheader("Backtest Summary :")
        with placeholder5.container():
            st.write("Buy Only(After Commissions) : ",df['Net Buy(After Commissions)'].iloc[0])
            st.write("Sell Only(After Commissions) : ",df['Net Sell(After Commissions)'].iloc[0])
            st.write("Number of Trades : ",df['Trades'].iloc[0])
            st.write("Total commissions : ",df['Total Commissions'].iloc[0])
            st.write("Total PnL(After Commissions) : ",df['Net PnL(After Commissions)'].iloc[0])
            st.write("Buy Only ROI(%) : ",df['Buy ROI(%)'].iloc[0])
            st.write("Total Buy & Sell ROI(%) : ",df['Total Buy/Sell ROI(%)'].iloc[0])
            st.write("Buy & Hold PnL : ",df['Buy & Hold PnL'].iloc[0])
            st.write("Buy & Hold ROI(%) : ",df['Buy Hold ROI(%)'].iloc[0])
        #placeholder4.write(df)
        trades=trades[['Symbol','Signal','Entry Date','Entry Time','Exit Date','Exit Time','Entry','Exit','Net Points Captured(After Commissions)','Total PnL(After Commissions)','Buy Only PnL(After Commissions)','ROI(%)']]
        trades.reset_index(drop=True,inplace=True)
        trades.index += 1 
        trades=trades.round(2).astype(object)
        placeholder6.subheader("List of Trades :")
        st.write(trades)
        #placeholder6.pyplot()
        st.markdown(get_table_download_link(trades), unsafe_allow_html=True)
    else:
        trades=trades[['Symbol','Signal','Net Points Captured(After Commissions)','Entry Date','Entry Time','Exit Date','Exit Time','Entry','Exit','ROI(%)']]
        #trades=trades[['Symbol','Signal','Entry Date','Entry Time','Exit Date','Exit Time','Entry','Exit','Net Points Captured','ROI(%)']]
        df=trades
        df=df.iloc[::-1]
        df=df.reset_index(drop=True)
        df.index += 1 
        df=df.round(2).astype(object)
        if df.empty==False:
            placeholder5.subheader("List of recently Closed Trades :")
            placeholder6.write(df.head(10),use_container_width=True)
    
    

    

def datafeed(mult,commission,start_date,end_date,mode,stop=False,
resolution="1m",
tick='BTCUSD',
exc='Bitstamp',
indicator=1,
future=0,
mag=100,
ma_len=50,
fastMa=5,
midMa=20,
slowMa=200,
atrlen=10,
superMult=3,
psarAf=0.02,
psarMaxAf=0.2,
waitTime=30):
    data=0
    resolution=timePeriodFormatter(resolution)
    global plots
    chartTitle=tick
    count=1
    while(stop!=True):
        clear_output(wait=True)
        df=data
        message.empty()                
        try:
            if(future==1 or future==2):
                data=tv.get_hist(tick, exc,interval=resolution,n_bars=5000,fut_contract=future)
                chartTitle=tick+" "+str(future)+"!"
            else:
                data=tv.get_hist(tick, exc,interval=resolution,n_bars=5000)
        except:
            message.error('Connection Error Retrying')
            time.sleep(waitTime)
            if(count==1):
                pass
            data=df
        data.round(2)
        buyHold=0
        if mode=='Backtesting':
            data.reset_index(inplace=True)
            data['date']=data['datetime'].dt.date
            data=data[(data['date']>=start_date) & (data['date']<=end_date)]
            buyHold=data['close'].iloc[-1]-data['open'].iloc[0]

        if(indicator==1):
            data, plots=ma(data,ma_len,"ema",mag)
        elif(indicator==2):
            data, plots=ma(data,ma_len,"wma",mag)
        elif(indicator==3):
            data, plots=ftsma(data,fastMa,midMa,slowMa,mag)
        elif(indicator==4):
            data, plots=supertrend(data,atrlen, superMult,mag)
        elif(indicator==5):
            data, plots=psar(data,psarAf,psarMaxAf)
        else:
            data, plots=ma(data,ma_len,"ema",mag)
        if mode=='Backtesting':
            backtest(data,start_date,end_date,commission,mult=mult,flag=1,buyHold=buyHold)
            break
        
        plots = [x for x in plots if np.isnan(x['data']).all() == False]
        
        placeholder1.pyplot(mpf.plot(data.tail(mag),hlines=dict(hlines=[data['close'].iloc[-1]],colors=['b'],linestyle='-.'),type='candle',style='yahoo',title = chartTitle,tight_layout=True,addplot=plots,figsize=(8, 3)))
        lstRef="Last Chart Refresh - "+str(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-4])
        placeholder2.text(lstRef)
        placeholder3.subheader("Currently Open Trade :")
        #placeholder4.write(currTrade(data),use_container_width=False)
        df=currTrade(data,commission,mult)
        #tradeOutput=["Symbol","Signal",'Entry Date','Entry Time','Current Date','Current Time',"Entry Price",'Current Price',"Net Points Captured","ROI(%)"]
        with placeholder4.container():
            st.write("Symbol : ",df['Symbol'].iloc[0])
            st.write("Signal : ",df['Signal'].iloc[0])
            st.write("Entry Date : ",df['Entry Date'].iloc[0])
            st.write("Entry Time : ",df['Entry Time'].iloc[0])
            st.write("Last Change Date : ",df['Current Date'].iloc[0])
            st.write("Last Change Time : ",df['Current Time'].iloc[0])
            st.write("Entry Price : ",df['Entry Price'].iloc[0])
            st.write("Last Price : ",df['Current Price'].iloc[0])
            st.write("Net Points Captured (After Commissions): ",df['Net Points Captured'].iloc[0])
            st.write("Current ROI(%) : ",df['ROI(%)'].iloc[0])
        backtest(data,comm=commission,mult=mult)
        #time.sleep(waitTime)
        count+=1
def main():
    datafeed(mult,commission,start_date,end_date,mode,stop,timePeriod,tick,exc,indicator,future,mag,ma_len,fastMa,midMa,slowMa,atrlen,superMult,psarAf,psarMaxAf,waitTime)


st.set_page_config(layout="wide")
st.title('Velo-ct Trading')
mark=st.markdown("""
  Use the menu on the left to select data and set plot parameters, and then click Start
""")
mult=1
stop=False
timePeriod="1"
tick='TCS'
exc='NSE'
future=0
waitTime=1
mode='Live Trades'
indicator=1
if 'futFlag' not in st.session_state:
    st.session_state['futFlag'] = 0

# 1   -   EMA
# 2   -   WMA
# 3   -   FTSMA
# 4   -   SuperTrend
# 5   -   Parabolic SAR

mag=100
ma_len=50

fastMa=5
midMa=20
slowMa=200

atrlen=5
superMult=1

psarAf=0.02
psarMaxAf=0.2

commission=0.0
today=tommorow=0
end_date=datetime.date.today()
start_date=end_date-datetime.timedelta(days=10)

mode = st.sidebar.selectbox('Select Mode:', ( "Live Trades","Backtesting"))


segment=st.sidebar.selectbox('Segment:', ("Equity","Future"))

tickFile = Path(__file__).parents[1] / 'FrontEnd/TickerList.csv'
df=pd.read_csv(tickFile)
df=df[['Symbol','Company Name']]



fnoFile = Path(__file__).parents[1] / 'FrontEnd/FnOList.csv'
fno=pd.read_csv(fnoFile)
fno['Symbol']=fno['SYMBOL']
fno=fno['Symbol']

if segment=='Future':
    df=df.merge(fno,how='right')

tick = st.sidebar.selectbox('Ticker:', df['Company Name'])
tick=df.loc[df['Company Name']==tick,'Symbol']
tick=tick.tolist()
tick=tick[0]


if segment=='Future':
    option = st.sidebar.selectbox('Select Expiry',('Current Month Expiry', 'Next Month Expiry'))
    if(option=="Current Month Expiry"):
        future=1
    else:
        future=2
#exc = st.sidebar.text_input('Exchange:', 'NSE')
exc='NSE'


indicatorSelect = st.sidebar.radio("Select Indicator :",('E Velo-ct', 'W Velo-ct', 'F Velo-ct','S Velo-ct','P Velo-ct'))



if indicatorSelect == 'E Velo-ct':
    indicator=1
elif indicatorSelect == 'W Velo-ct':
    indicator=2
elif indicatorSelect == 'F Velo-ct':
    indicator=3
elif indicatorSelect == 'S Velo-ct':
    indicator=4
elif indicatorSelect == 'P Velo-ct':
    indicator=5
else:
    indicator=1

timePeriod = st.sidebar.selectbox('Select Time Period:', ( "30m","1m","3m","5m","15m","45m","1H","2H","3H","4H","1D","1W","1M"))



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#picFile = Path(__file__).parents[1] / 'FrontEnd/stockpic.jpg'
#image = Image.open(picFile)
#placeholder1 = st.image(image)

if mode=="Live Trades":
    mag = st.sidebar.slider('Chart Magnification :', 1, 200, 100,help="Number of candles displayed in the live chart")
else:
    testDur = st.sidebar.selectbox('Select Backtest Duration:', ("1W","1D","1M","3M","6M","1Y"),help="The maximum historical data available for any time period is 5000 candles. Any duration longer than that will default to the maximum data available.")
    if(testDur=='1D'):
        start_date=end_date-datetime.timedelta(days=1)
    elif(testDur=='1W'):
        start_date=end_date-datetime.timedelta(days=7)
    elif(testDur=='1M'):
        start_date=end_date-datetime.timedelta(days=30)
    elif(testDur=='3M'):
        start_date=end_date-datetime.timedelta(days=90)
    elif(testDur=='6M'):
        start_date=end_date-datetime.timedelta(days=180)
    elif(testDur=='1Y'):
        start_date=end_date-datetime.timedelta(days=365)
    else:
        start_date=end_date-datetime.timedelta(days=30)
    start_date = st.sidebar.date_input('Start date', start_date,help="The maximum historical data available for any time period is 5000 candles. Any start date predating that would default to the earliest data available.")
    end_date = st.sidebar.date_input('End date', end_date)
    if start_date > end_date:
        st.sidebar.error('Error: End date must fall after start date.')
commission = st.sidebar.number_input('Enter Commission per trade (% of Contract):',value=0.05,help="The value is % of contract bought.This commission is charged on each buy and sell order executed i.e a roundtrip will cost 2x this value.")
mult = st.sidebar.number_input('Number of Units',value=1,min_value=1,help="This is the number of contracts that you wish to buy/sell. Commisions and PnL will be multiplied accordingly.")
commission*=2
   
start_button = st.sidebar.empty()
stop_button = st.sidebar.empty()
#with st.spinner('Wait for it...'):
#time.sleep(5)
#st.success('Done!')

st.set_option('deprecation.showPyplotGlobalUse', False)
message=st.empty()

placeholder1 = st.empty()
placeholder2=st.empty()
placeholder3=st.empty()
placeholder4=st.empty()
placeholder5=st.empty()
placeholder6=st.empty()


if start_button.button('start',key='start'):
    start_button.empty()
    mark.empty()
    if stop_button.button('stop',key='stop'):
        pass
    main()
    
    