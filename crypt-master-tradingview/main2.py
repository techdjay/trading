import asyncio
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


def generate_csv(a, filename):
    out = re.search('"s":\[(.+?)\}\]', a).group(1)
    x = out.split(',{\"')
    if len(x) < 50:
        print(f"{filename} less than 50")
        return
    os.makedirs(os.path.join("data1", re.match("[A-Z]*", filename).group()), exist_ok=True)
    with open(os.path.join("data1", re.match("[A-Z]*", filename).group(), f'{filename}.csv'), mode='w',
              newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
        for xi in x:
            xi = re.split('\[|:|,|\]', xi)
            # print(xi)
            ind = int(xi[1])
            ts = datetime.fromtimestamp(float(xi[4])).strftime("%Y-%m-%d %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])
    print(f"save {filename}")


headers = json.dumps({
    'Origin': 'https://data.tradingview.com'
})

crypts = config["crypts"]
deltas = config["deltas"]
L60 = config["60"]
less = 5


async def main(crypts, delta):
    try:
        try:
            ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=headers)
            print("connected")
        except Exception as e:
            print(repr(e))
            time.sleep(3)
            ws = create_connection('wss://data.tradingview.com/socket.io/websocket', headers=headers)
        for crypt in crypts:
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
            sendMessage(ws, "resolve_symbol", [chart_session, "symbol_1",
                                                     "={\"symbol\":\"" + "NSE:" + crypt + "SBIN" + "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
            sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", delta, 8000])
            while True:
                try:
                    # result = asyncio.wait_for(ws.recv(), timeout=1)
                    result = ws.recv()
                    if "timescale_update" in result:
                        generate_csv(result, crypt + delta)
                        break
                except Exception as e:
                    print(repr(e))
                    break
        time.sleep(0.1)
    except Exception as e:
        print(repr(e))
        pass
    try:
        ws.close()
    except Exception as e:
        print(repr(e))
        time.sleep(0.1)
async def main_task():
    while True:
        tasks = crypts + L60
        await asyncio.gather(*[main(x, "5") for x in
                               [tasks[i:i + 5 if (i + 5) < len(tasks) else len(tasks)] for i in
                                range(5, len(tasks), 5)]])
        if datetime.now().minute % less != 0:
            resiual = datetime.now().minute % less
            print(f"current {datetime.now()} next time {less - resiual} minute")
            await asyncio.sleep((less - resiual) * 60)
        else:
            await asyncio.sleep(60*less)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_task())
