import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os
from core.emailSender import send
from datetime import datetime
import asyncio
import json
import re



DATADIR = "data"
SAVEDIR = "analysis"
delta = "60"
win = 18
m = 3
offset1 = -350
deltas = [2,4,6,8,10,12]

loop = asyncio.get_event_loop()
def dataset(select=None):
    for files in glob(DATADIR + "/*"):
        for file in glob(files + "/*"):
            if select:
                for s in select:
                    if s in file:
                        break
                else:
                    continue
            df = pd.read_csv(file, index_col=0)
            if df.empty or df.shape[0] < 100:
                print(f"empty {file} ")
                continue
            df.reset_index(drop=True)
            df.set_index(["date"], inplace=True)
            df = df[offset1:]
            for i in deltas:
                df[i] = df["close"].rolling(i).mean().fillna(0).copy()
            df = df[20:]
            yield df, file.split(os.sep)[-1].split(".")[0]


def warn_local(imgs):
    os.makedirs(os.path.join("warn"),exist_ok=True)




def analysis():
    gen = dataset(select=["15"])
    # gen = dataset(select=["30","60"])
    p15 = {}
    p30 = {}
    p60 = {}
    for data, name in gen:
        x = np.array(list(range(data.shape[0]))).reshape([-1, 1])
        # for i in deltas:
        warnp = {}
        for i in deltas:
            plt.figure(figsize=(26, 13))
            tittle = name + '_MA' + str(i)
            if i == deltas[0]:
                data.reset_index(inplace=True)
            data.loc[:,"redate"] = np.copy(data["date"].iloc[::-1])
            data.loc[:,"re" + str(i)] = np.copy(data[i].iloc[::-1])
            plt.scatter(x, data["close"], color='yellowgreen', label="training data")
            plt.xticks(np.squeeze(x)[::20],[x[5:-3] for x in data.date[::20].values.tolist()])
            # plt.xticks(x.reshape([1,-1])[0], [1]*x.shape[0], rotation='vertical')
            # plt.scatter(x, data["close"], color='yellowgreen', label="training data")
            # plt.plot(prey,c="red",label="predict")
            plt.plot(data[i].values, label="ma" + str(i))
            der = data[i] - data[i].shift(1)
            data[i].mean()
            offset = data[i].mean() * 0.7

            plt.scatter(x, der.values * 10 + offset, label="derivation", c=der > 0)
            plt.plot(data["close"],color="hotpink")

            temp = (der > 0).values[::-1]
            data.loc[:,"der"] = np.copy(der.values[::-1])
            data.loc[:,"reclose"] = np.copy(data["close"].iloc[::-1])
            for ix in range(temp.shape[0] - 8):
                tx = temp[ix:ix + 5]
                if (sum(tx) == 4 and tx[2] == False) or (sum(tx) == 1 and tx[2] == True):
                    temp[ix + 2] = not temp[ix + 2]
            data.loc[:,"blocks"] = np.copy((der>0).values[::-1])
            data.loc[:,"anchors"] = data["blocks"] == data["blocks"].shift(1)
            blocks = []
            t = []
            anchor = 0
            anchors = data["anchors"][data["anchors"] == False].index
            means = []
            plt.plot(der.values * 10 + offset, c="cyan", label="derivation")
            for index in anchors[1:]:
                # data["low"][data["low"] == 0.55721].index
                # if  index-anchor<3:
                #     blocks.append([-1]*(index-anchor))
                blocks.append(data["blocks"].iloc[anchor:index].values)
                means.append(data["der"].iloc[anchor:index].mean())
                if index - anchor>2:
                    plt.axvline(data.index[-index],color="lightsteelblue")
                anchor = index

            # plt.plot(der.values * 10 + offset, c="cyan", label="derivation")
            plt.axhline(y=offset, color='palevioletred', linestyle='-')

            path = os.path.join(SAVEDIR, re.match("[A-Z]*",name).group())
            os.makedirs(path, exist_ok=True)
            plt.legend(loc='upper left', title=data.index[-1])
            plt.title(tittle)
            try:
                dtime = datetime.strptime(data["redate"][0], "%Y-%m-%d %H:%M:%S")
            except:
                dtime = datetime.now()#strftime("%Y%m%d%H%M%S")
                print("fuck")
            timestr = dtime.strftime("%Y%m%d%H%M")
            savepath = os.path.join(path, f"{tittle}_{timestr}.jpg")
            print(f"save {savepath}")
            plt.savefig(savepath, bbox_inches='tight')
            # plt.show()
            plt.cla()

            # if len(blocks[1])>=3 and len(blocks[0]<3):


            describ = [tittle,"-".join(str(x) for x in anchors[:4]), timestr]
            if "15" in name:
                p15[name] = [describ, savepath]
            elif "30" in name:
                p30[name] = [describ, savepath]
            elif "60" in name:
                p60[name] = [describ, savepath]


            #warning 4 8 12
            if i != 10:
                warnp[tittle] = [describ, savepath]

            # start warning
            if i == 10 and "60" in name and len(blocks[0]) > 4 and abs(data["der"].iloc[0]) < abs(means[0]):
                print(f"warning {name}")
                warnp[tittle] = [describ, savepath]
            elif i == 10:
                break
        else:
            warnp["isup"] = bool(means[0]>0)
            loop.run_in_executor(None,warn_local,warnp)
            # loop.run_in_executor(None,send,warnp)
            loop.run_in_executor(None,insert_record,{"name":tittle,"time":dtime,"predict":int(means[0]>0),"describe":json.dumps(warnp)})

    # send(p15)
    # send(p30)
    # send(p60)
