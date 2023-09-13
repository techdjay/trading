import cryptocompare as cryp
import datetime
from core import configure
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
import cryptocompare as cryp
from core import DBUtils


SAVEDIR = os.path.join(os.path.dirname(os.path.abspath(".")),"data")
synthi = [1,4]

import queue

loop = asyncio.get_event_loop()

q = queue.Queue()
def redo(future):
    global q
    if future.result():
        print(f"redo {future.result()}")
        q.put(future.result())


def work(cry):
    data = None
    print(cry)
    while data is None:
        data = cryp.get_historical_price_minute(cry, currency='USDT', exchange="CCCAGG", limit=6)
    for d in data:
        time = datetime.datetime.fromtimestamp(d["time"])
        d.update({"time": time, "unit": "minute", "name": cry})
        DBUtils.insert_cryp(d)


first = 0
less = 14
interval =5
offset = 0
secondoffset = 5
def main(q):
    first = True
    while True:
        now = datetime.now()
        resiual = now.minute % interval
        start = time.time()
        for cry in config["crypts"]:
            loop.run_in_executor(None,work,cry)
        delta = time.time() - start
        print(f"#######startAt {now} process cost {delta}")
        stime = abs(interval - resiual + offset)
        ws = stime * 60 - now.second - delta + secondoffset
        cur = datetime.now()
        nexttime = cur + dt.timedelta(seconds=ws)
        # print(f"#######current {datetime.now()} next time {stime} minute - {now.second} - {delta} + {secondoffset}")
        print(f"#######current {datetime.now()} next time {nexttime}")
        time.sleep(ws)

threading.Thread(target=main,args=(q,)).start()
loop.run_forever()