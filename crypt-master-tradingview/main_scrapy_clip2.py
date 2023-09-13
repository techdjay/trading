import asyncio
import threading
import time
import glob
from websocket import create_connection
import json
import random
import string
import re
import pandas as pd
import csv
from datetime import datetime
import os
from core.modeling import analysis
from core.configure import config
import datetime as dt

def filter_raw_message(text):
    try:
        found = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        print(found)
        print(found2)
        return found, found2
    except AttributeError:
        print("error")

def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string

def generateChartSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" + random_string

def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

def constructMessage(func, paramList):
    # json_mylist = json.dumps(mylist, separators=(',', ':'))
    return json.dumps({
        "m": func,
        "p": paramList
    }, separators=(',', ':'))

def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

def sendRawMessage(ws, message):
    ws.send(prependHeader(message))

def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

def generate_csv1(a, filename):
    out = re.search('"s":\[(.+?)\}\]', a).group(1)
    x = out.split(',{\"')
    if len(x) < 50:
        print(f"{filename} less than 50")
        return
    os.makedirs(os.path.join("data", re.match("[A-Z]*", filename).group()), exist_ok=True)
    with open(os.path.join("data", re.match("[A-Z]*", filename).group(),
                           f'{filename}.csv'), mode='w',
              newline='') as data_file:
        # with open(os.path.join("data", re.match("[A-Z]*", filename).group(),
        #                        f'{filename}_{datetime.now().strftime("%Y%m%d%H%M")}.csv'), mode='w',
        #           newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
        for xi in x:
            xi = re.split('\[|:|,|\]', xi)
            # print(xi)
            ind = int(xi[1])
            ts = datetime.fromtimestamp(float(xi[4])).strftime("%Y-%m-%d %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])
    print(f"save {filename}")

def save_df(df,name):
    df.to_csv(name)

def generate_csv(a, crypt,delta):
    filename = crypt+delta
    out = re.search('"s":\[(.+?)\}\]', a).group(1)
    x = out.split(',{\"')
    # if len(x) < 50:
    if len(x) < 50:
        print(f"{filename} less than 50")
        return  [delta,(crypt,)]
    os.makedirs(os.path.join("data", re.match("[A-Z]*", filename).group()), exist_ok=True)

    col = ['date', 'open', 'high', 'low', 'close', 'volume']
    ls = []
    for xi in x:
        xi = re.split('\[|:|,|\]', xi)
        # print(xi)
        # ind = int(xi[1])
        ts = datetime.fromtimestamp(float(xi[4])).strftime("%Y-%m-%d %H:%M:%S")
        ls.append([ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])
    df = pd.DataFrame(ls,columns=col)
    df.drop(axis=1,index=df.index[-1],inplace=True)
    cname = re.match("[A-Z]*", filename).group()
    if "DOT"  in filename:
        print("fuck")
    for n in config["synth"].get(delta):
        dlt,n = list(map(int,n.split("X")))
        tdf = df.copy()
        clipnd = config["clip"].get(str(dlt))
        if clipnd and n in clipnd:
            t = datetime.strptime(tdf.iloc[-1, :]["date"], "%Y-%m-%d %H:%M:%S")
            t +=  dt.timedelta(seconds=60*30)
            if not (t.hour * 60 *60 + t.minute) % (int(n)*int(dlt)) ==0:
                print(f"skip {cname} {n}")
                continue
            # if t.minute ==0:
            #     tdf = tdf.drop(axis=1, index=df.index[-1])
            # t = datetime.strptime(tdf.iloc[-1, :]["date"], "%Y-%m-%d %H:%M:%S")
            # if n >2:
            #     resiual = (t.hour % (n//2))+1
            #     tdf = tdf.drop(axis=1, index=tdf.index[-resiual*2:])
        savename = os.path.join("data",cname , f'{filename}X{n}.csv')
        print(f"save {savename}")
        if n == 1:
            # df.to_csv(savename,index=False)
            loop.run_in_executor(None,save_df,tdf,savename)
            continue
        synth = []
        indexs = tdf.index.to_numpy()[::-1]
        for i in range(tdf.shape[0] // n - 1):
            item = tdf.iloc[indexs[i * n + n - 1]:indexs[i * n] + 1]
            t = []
            t.append(item.iloc[0, 0])
            t.append(item.iloc[0, 1])
            t.append(item["high"].max())
            t.append(item["low"].min())
            t.append(item["close"].iloc[-1])
            synth.insert(0, t)
        # print(item.shape)
        tdf = pd.DataFrame(synth, columns=["date", "open", "high", "low", "close"])
        # tdf.to_csv(savename)
        loop.run_in_executor(None, save_df,tdf, savename)
    return None




headers = json.dumps({
    'Origin': 'https://data.tradingview.com'
})

# crypts = config["crypts"]
crypts = ["XRP","LINK","ETH","BTC","EOS","DOGE","ZEC","BCH","LOL","LTC","MATIC","UNI","1INCH","FIL","IOST","QTUM","SUSHI","NODE","SWFTC","STORJ","TRX","BTT","ETC"]
crypts = config["60"][:]
# synthi = config["synth"]
synthi = [1,4]



import queue
first = 0
less = 14
interval =5
offset = 0
secondoffset = 10
loop = asyncio.get_event_loop()

q = queue.Queue()
def redo(future):
    global q
    if future.result():
        print(f"redo {future.result()}")
        q.put(future.result())

def main(q):
    first = True
    while True:
        now = datetime.now()
        resiual = now.minute % interval
        start = time.time()

        try:
            ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=headers)
        except:
            time.sleep(3)
            continue
        try:
            # crypts += L60
            # for crypt in crypts:
            #     for delta in deltas:
            for k,v in config["simple"].items():
                q.put((k,v))
            while q:
                try:
                    delta,v = q.get_nowait()
                    print("new task:",delta,v)
                except Exception as e:
                    print(repr(e))
                    first = False
                    break
                if not first and (now.minute % int(delta)) > 3:
                    continue

                for crypt in v:
                    # if crypt in L60 and delta != "60":
                    #     continue
                    session = generateSession()
                    chart_session = generateChartSession()
                    sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
                    sendMessage(ws, "chart_create_session", [chart_session, ""])
                    sendMessage(ws, "quote_create_session", [session])
                    sendMessage(ws, "quote_set_fields",
                                [session, "ch", "chp", "current_session", "description", "local_description",
                                 "language",
                                 "exchange",
                                 "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name",
                                 "pricescale",
                                 "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp",
                                 "rtc"])
                    TEMP = "HUOBI:" + crypt
                    # if crypt == "FTI":
                    #     TEMP = "BINANCE:" + crypt

                    sendMessage(ws, "resolve_symbol", [chart_session, "symbol_1",
                                                       "={\"symbol\":\"" + TEMP + "USDT" + "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])

                    sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", delta, 8000])
                    while True:
                        try:
                            # result = asyncio.wait_for(ws.recv(), timeout=1)
                            result = ws.recv()
                            if "timescale_update" in result:
                                # loop = asyncio.get_event_loop()
                                future = loop.run_in_executor(None,generate_csv,result,crypt,delta)
                                future.add_done_callback(redo)
                                # generate_csv(result, crypt + delta)
                                break
                        except Exception as e:
                            print(repr(e))
                            break
            time.sleep(0.1)
        except:
            try:
                ws.close()
            except Exception as e:
                print(repr(e) + "already????????????")
            time.sleep(0.1)
            # ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=headers)
        print(datetime.now())
        try:
            ws.close()
        except:
            time.sleep(0.1)
        delta = time.time() - start
        print(f"#######startAt {now} process cost {delta}")
        stime = abs(interval - resiual + offset)
        ws = stime * 60 - now.second - delta + secondoffset
        cur = datetime.now()
        nexttime = cur + dt.timedelta(seconds=ws)
        # print(f"#######current {datetime.now()} next time {stime} minute - {now.second} - {delta} + {secondoffset}")
        print(f"#######current {datetime.now()} next time {nexttime}")
        time.sleep(abs(ws))

threading.Thread(target=main,args=(q,)).start()
loop.run_forever()