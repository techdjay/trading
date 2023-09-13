# from core.modeling import analysis
import glob
import json
import logging
import os
import threading
from pathlib import Path

import uvicorn
import queue
from fastapi import FastAPI, Form, Cookie
from core.modeling60min2 import analysis
import time
from core.configure import config
from core.configure import dog
from core import configure
from datetime import datetime
from fastapi import FastAPI, File, Form, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from core.webbuilder import build
from core.DBUtils import get_warn,get_warn2


logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("QED.log")
fh.setLevel(logging.ERROR)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
datadir = os.getcwd()
interval = 1
secondoffset = 0
offset = 2
import datetime as dt

# Session = namedtuple('Session', ["sess", "input", "output", "categories", "load_time"])

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/blocks", StaticFiles(directory="blocks"), name="blocks")
sessions = {}

T = "http://127.0.0.1:9311/blocks/XRP/30X1/XRP30X1_202105-29-11-02.jpg"
DATA_DIR = "blocks"

@app.get("/data")
def view_classes():
    """List classes"""
    t = os.listdir(DATA_DIR)
    t.sort(key=lambda x:x)
    ret = []
    for f in t:
        i30 = sorted(glob.glob(os.path.join(DATA_DIR, f,"15X1"+"/*")),key=os.path.getmtime)
        iden = i30[-1].split(os.sep)[-1]
        idens = iden.split("_")
        temp = {}
        temp["name"]= f
        temp["count"] = len(glob.glob(os.path.join(DATA_DIR, f + "/*")))
        temp["tend"] =idens[-2]
        temp["steps"] = idens[-1]
        ret.append(temp)
    return ret


@app.get("/group")
def view_groups():
    """List group"""
    ret = [
        {"name": k, "count": len(v),"check":v.get("check",False)}
        for k,v in configure.dog.items()
    ]
    ret.sort(key=lambda x:x["name"].split("@")[-1])
    ret.reverse()
    return ret

@app.get("/group/{name}",response_class=HTMLResponse)
def view_group(name:str):
    """List group"""
    para = name.split("@")
    group = configure.dog[name]
    try:
        group.pop("check")
    except:
        pass
    ret = [
        {"name": k, "url":v} if k != "check" else None
        for k,v in configure.dog[name].items()
    ]
    group["check"] = True
    configure.dog.update({name:group})
    persist(configure.dog)
    ret.reverse()
    return build(ret)


@app.get("/data/{name}")
def view_class(name: str):
    """Get class information"""
    # if name[-1].isdigit() and len(name.split("X")) ==2:
    t = name.split("+")
    if len(t)==2:
        ret = []
        for f in glob.glob(os.path.join(DATA_DIR, t[0],t[1], "*.jpg")):
            item = {}
            file_name = os.path.basename(f)
            # item["url"] = f"/files/images/{name}/{file_name}"
            item["url"] = f"/{DATA_DIR}/{t[0]}/{t[1]}/{file_name}"
            item["id"] = f"{file_name.rpartition('.')[0]}"
            ret.append(item)
        print(ret)
        return ret
    else:
        ret = []
        for f in os.listdir(os.path.join(DATA_DIR,name)):
            paths = sorted(Path(os.path.join(DATA_DIR, name, f )).iterdir(), key=os.path.getmtime)
            # fn = list(glob.glob(os.path.join(DATA_DIR, name, f + "/*")))[-1]
            fn=paths[-1]
            item = {}
            file_name = os.path.basename(fn)
            item["url"] = f"/{DATA_DIR}/{name}/{f}/{file_name}"
            item["name"] = file_name
            ret.append(item)
        return ret


@app.get("/webview/{name}", response_class=HTMLResponse)
async def webview(name):
    ret = []
    for f in os.listdir(os.path.join(DATA_DIR, name)):
        paths = sorted(Path(os.path.join(DATA_DIR, name, f)).iterdir(), key=os.path.getmtime)
        # fn = list(glob.glob(os.path.join(DATA_DIR, name, f + "/*")))[-1]
        fn = paths[-1]
        item = {}
        file_name = os.path.basename(fn)
        item["url"] = f"/{DATA_DIR}/{name}/{f}/{file_name}"
        item["name"] = file_name
        item["index"] = f
        ret.append(item)
    ret = sorted(ret, key=lambda x: list(map(int, x["index"].split("X"))))
    return build(ret)


@app.get("/webviewbrowser/{name}", response_class=HTMLResponse)
async def webview(name):
    ret = []
    for f in os.listdir(os.path.join(DATA_DIR, name)):
        paths = sorted(Path(os.path.join(DATA_DIR, name, f)).iterdir(), key=os.path.getmtime)
        # fn = list(glob.glob(os.path.join(DATA_DIR, name, f + "/*")))[-1]
        fn = paths[-1]
        item = {}
        file_name = os.path.basename(fn)
        item["url"] = f"/{DATA_DIR}/{name}/{f}/{file_name}"
        item["name"] = file_name
        item["index"] = f
        ret.append(item)
    ret = sorted(ret,key=lambda x:list(map(int,x["index"].split("X"))))
    return build(ret,True)

# @app.get("/data/{name}")
# def view_class(name: str):
#     """Get class information"""
#     # if name[-1].isdigit() and len(name.split("X")) ==2:
#     t = name.split("+")
#     if len(t)==2:
#         ret = []
#         for f in glob.glob(os.path.join(DATA_DIR, t[0],t[1], "*.jpg")):
#             item = {}
#             file_name = os.path.basename(f)
#             # item["url"] = f"/files/images/{name}/{file_name}"
#             item["url"] = f"/{DATA_DIR}/{t[0]}/{t[1]}/{file_name}"
#             item["id"] = f"{file_name.rpartition('.')[0]}"
#             ret.append(item)
#         print(ret)
#         return ret
#     else:
#         ret = [
#             {"name": f, "count": len(glob.glob(os.path.join(DATA_DIR,name, f + "/*")))}
#             for f in os.listdir(os.path.join(DATA_DIR,name))
#         ]
#         return ret

@app.post("/warn")
async def root(data: str = Form(...)):
    logger.info("postwarn")
    result = ""
    warns = json.loads(data)
    for v in warns:
        result += v["name"] + "_"

    now = time.time()
    q.put(str(now)+"-"+result)

    return {"message": result}

@app.get("/info")
async def getwarn():
    logger.info("getwarn")
    try:
        result = configure.q.get_nowait()
        print(result)
        return {"message": result}
    except Exception as e:
        print(repr(e))
        return {"message":-1}


@app.post("/echo/{name}")
async def postEchoApi(name:str,age:str,text:str=Cookie(None)):
    return {"echo":text,"name":name,"age":age}

@app.get("/fuck/{fuck_id}")
async def testapi(fuck_id):
    return {"message": fuck_id}


def persist(data):
    with open(os.path.join(datadir, "dog1.json"), "w+") as f:
        # WARNING = json.load(f)
        print("save WARNING:" ,datadir)
        json.dump(data.copy(), f)

def watchdog(q):
    while True:
        now = datetime.now()
        # resiual = now.minute % interval
        start = time.time()

        for i in config["watch"]:
            result = get_warn2({"delta":i,"time":now-dt.timedelta(hours=29)})
            if result:
                if list(result.keys())[0] not in configure.dog.keys():
                    configure.dog.update(result)
                    print(result)
                    persist(configure.dog)
                    q.put(str(start) + "-" + list(result.keys())[0])


        # delta = time.time() - start
        # print(f"#######startAt {now} process cost {delta}")
        # stime = abs(interval - resiual + offset)
        # ws = stime * 60 - now.second - delta + secondoffset++++++++---
        # cur = datetime.now()
        # nexttime = cur + dt.timedelta(seconds=ws)
        # # print(f"#######current {datetime.now()} next time {stime} minute - {now.second} - {delta} + {secondoffset}")
        # print(f"#######check current {datetime.now()}")
        time.sleep(10)


if __name__ == '__main__':
    print("fuck2")
    try:
        print("load warns")
        with open(os.path.join(datadir, "dog1.json"), "r") as f:
            configure.dog = json.load(f)
    except:
        pass
    print(configure.dog)
    threading.Thread(target=watchdog,args=(configure.q,)).start()
    uvicorn.run(app='main:app', host="0.0.0.0", port=9311,workers=0, reload=False)
