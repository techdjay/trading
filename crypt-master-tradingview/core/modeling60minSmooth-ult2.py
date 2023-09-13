import concurrent
import multiprocessing
import time

import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os
# from core.emailSender import send
import requests

from core.emailSender2 import send
from datetime import datetime
import asyncio
from core.DBUtils import insert_warn
import json
import re
from core.blocksearch import bsearch
from matplotlib.collections import LineCollection
from core.configure import config
# from sklearn.metrics.pairwise import cosine_similarity,cosine_distances

import datetime as dt

DATADIR = os.path.join(os.path.dirname(os.path.abspath(".")),"data")
SAVEDIR = os.path.join(os.path.dirname(os.path.abspath(".")),"blocks")
delta = "60"
win = 11
unit = -160
deltas = list(range(1, win))
deltas = config["deltas"]
# deltas = [8, 4, 5]
totalvotes = 3
loop = asyncio.get_event_loop()
warndir = config["warndir"]

def dataset(select=None, crypts=None):
    for files in glob(DATADIR + "/*"):
        for file in glob(files + "/*"):
            if select is not None:
                for s in select:
                    if s in file:
                        if s.startswith("5X") and "15X" in file:
                            continue
                        break
                else:
                    continue
            if crypts is not None:
                for c in crypts:
                    if c in file:
                        break
                else:
                    continue
            try:
                df = pd.read_csv(file, index_col=0)
                num = re.findall('\d+', file)
                # offset = -unit*(int(num[-1]))
                if df.empty or df.shape[0] < 10:
                    print(f"empty {file} ")
                    continue
                df.reset_index(drop=True)
                df.set_index(["date"], inplace=True)
                df = df.iloc[unit:, :]
                vote = pd.DataFrame()
                pch = pd.DataFrame()
                ma = pd.DataFrame()
                pc = (df["close"] - df["open"]) / df["open"]
                actual_pch = (df["close"] / df["close"].shift(1) - 1).values * 100
                actual_pch = np.round(actual_pch, 1)
                for i in deltas:
                    ma[i] = df["close"].rolling(i).mean().fillna(0).copy()
                    df[i] = ma[i]
                    pch[i] = (df[i] / df[i].shift(1) - 1).round(4) * 100
                    vote[i] = (df[i] - df[i].shift(1)) > 0

                ma["mean-ma"] = ma.mean(axis=1)
                M = ma.shape[0]
                N = 2
                shifts = N - 1
                d = smooth(ma["mean-ma"], N)
                ma["smoothma"] = np.concatenate([[d[0]] * shifts, d])
                ma["smoothma-diff"] = ma["smoothma"] - ma["smoothma"].shift(1)
                rd = smooth(df["close"], N)
                ma["smoothraw"] = np.concatenate([[rd[0]] * shifts, rd])
                ma["smoothraw-diff"] = ma["smoothraw"] - ma["smoothraw"].shift(1)
                df = df.iloc[20:, :]
                rows = df.shape[0]
                yield df, file.split(os.sep)[-1].split(".")[0], vote.iloc[-rows:, :], pch.iloc[-rows:, :], actual_pch[
                                                                                                           -rows:], ma.iloc[
                                                                                                                    -rows:,
                                                                                                                    :], pc.iloc[
                                                                                                                        -rows:]
            except Exception as e:
                print(repr(e))

datadir = os.getcwd()

# M = df.shape[0]
# N = 5
# shifts = df.shape[0] -( max(M, N) - min(M, N) + 1)
def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    # print(box)
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

def persist(data):
    with open(os.path.join(datadir, warndir), "w+") as f:
        # WARNING = json.load(f)
        print("save WARNING:" ,datadir)
        json.dump(data.copy(), f)

def httppost(data):
    d_order = list(filter(lambda x: any([j in x["name"] for j in config["email"]]) and all([k not in x["name"] for k in config["exclud"]]), data))
    if len(d_order) > 0:
        print("post")
        response = requests.post("http://else.so:9311/warn", data={"data": json.dumps(d_order)})
        print(response.text)

# delta = config["deltas"]
synth = config["synth"]
first = 1
DEBUG = "MATIC30X4"

def draw(se,crypts,WARNING):
    gen = dataset(select=se, crypts=crypts)
    global totalvotes
    temp = {}
    # WARNING = []
    offset = 0
    warns = []
    for data, name, vote, pch, actual_pch, ma, pc in gen:
        # if "60" in name and now.minute > 10:
        #     continue
        plt.figure(figsize=(36, 16))
        votes = []
        pchs = []
        mas = []
        for i in range(data.shape[0] - 1, -1, -1):
            # votes.insert(0, sum(vote.iloc[i, :]) - (win - sum(vote.iloc[i, :])))
            t = sum(vote.iloc[i, :])
            m = sum(ma.iloc[i, :])
            f = totalvotes - t
            votes.insert(0, t - f)
            pchs.insert(0, pch.iloc[i].mean())
            mas.insert(0, round(m / totalvotes, 2))
        tittle = name
        x = list(range(data.shape[0]))
        cur = WARNING.get(name, {})
        if not cur:
            WARNING[name] = []

        cryp = re.match("[A-Z]*", name).group()
        delta = name.split(cryp)[-1]
        path = os.path.join(SAVEDIR, cryp, delta)
        os.makedirs(path, exist_ok=True)

        temp = pd.DataFrame({"date": data.index, "votes": votes, "pchs": pchs, "mas": mas, "pc": pc})
        # ""
        temp["data"] = np.abs(temp["votes"]) * temp["pchs"]
        # temp["turn"] = temp["votes"].rolling(3).max() - temp["votes"].rolling(3).min()

        result = bsearch(temp["data"].values.reshape([-1, 1]), 1, 1)
        result = result[::-1]
        ax = plt.axes()
        bs = result[:, 1] > 0
        bs = np.append(bs, None)
        seg = [i if bs[i] != bs[i + 1] else None for i in range(len(bs) - 1)]

        # anchors
        seg = list(filter(None, seg))
        linecolors = ["mediumspringgreen" if bs[x] else "lightcoral" for x in seg]
        seg.insert(0, 0)
        blockx = np.uint16(result[:, 0]).tolist()
        segx = [blockx[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1] for i in range(len(seg) - 1)]
        segments = [[(x, 0) for x in sx] for sx in segx]
        ax.add_collection(LineCollection(segments, colors=linecolors, lw=1, alpha=0.7))

        scale = data["close"].max() - data["close"].min()
        minclose = data["close"].min()
        pscale = max(pchs) - min(pchs)

        f = lambda x: pscale * (x - minclose) / scale - pscale / 2
        turnscale_f = lambda r: (pscale * r) / ((win - 1) * 2)

        scale_actual_pch = list(map(turnscale_f, actual_pch))
        # scale close and mean 6
        scale_close = list(map(f, data["close"]))
        plt.plot(scale_close, label="close", alpha=0.7, lw=3, c="darkcyan")
        plt.scatter(x, scale_close, alpha=0.6, s=35, color='k')

        cliped = np.clip(scale_actual_pch, -8, 8)
        plt.bar(x, cliped,
                color=["lightgreen" if x > 0 else "cornflowerblue" for x in actual_pch[-offset:]],
                alpha=0.4)

        plt.plot(list(map(f, ma["mean-ma"])), color="c", alpha=0.5, label="mean-ma")

        # smoothmadiff = list(map(turnscale_f, ma["smoothma-diff"].values))
        smoothma = list(map(f, ma["smoothma"].values))
        scale1 = ma["smoothma"].max() - ma["smoothma"].min()
        min_ = ma["smoothma-diff"].mean()
        fsmoothmadiff = lambda x: 2 * pscale * (x) / scale1
        smoothmadiff = list(map(fsmoothmadiff, ma["smoothma-diff"].values))
        # smoothmadiff = ma["smoothma-diff"].values
        st = np.clip(np.array(smoothmadiff), -8, 8)
        plt.plot(st, "g-", label="smoothdiff", lw=2, alpha=0.9)
        plt.scatter(x, st, c=ma["smoothma-diff"] > 0)
        plt.plot(smoothma, "r-", lw=3, label="mean-ma-smooth", alpha=0.5)
        plt.scatter(x, smoothma)

        cross_smooth = bool(smoothmadiff[-1] * smoothmadiff[-2] < 0)
        tend_smooth = bool(smoothmadiff[-1] > 0)

        madiff = np.round(temp["mas"] - temp["mas"].shift(1), 2)
        madiff.fillna(0, inplace=True)
        minma = temp["mas"].min()
        mascale = temp["mas"].max() - temp["mas"].min()
        fma = lambda x: pscale * (x - minma) / mascale - pscale / 2

        for i in range(len(x)):
            plt.text(x[i], cliped[i],
                     actual_pch[i], alpha=0.5, fontsize=10,
                     color="indigo",
                     style="italic", weight="light")
        # bound
        plt.scatter([blockx[xx] for xx in seg], [0] * len(seg), alpha=0.5, label="bound")

        actual_block_return = [round(sum(actual_pch[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1]), 2) for i in
                               range(len(seg) - 1)]

        for i in range(len(seg) - 1):
            plt.text(blockx[seg[i]] + len(segments[i]) / 2, -pscale * 0.2,
                     actual_block_return[i], alpha=0.9, fontsize=20,
                     color="indigo",
                     style="italic", weight="light", rotation=45)

        xticks = [blockx[xx] for xx in seg]
        plt.xticks([blockx[xx] for xx in seg], data.index[xticks], rotation=45, color="dimgrey")
        plt.plot(temp["pchs"].iloc[-offset:], alpha=0.6, label="pch", c="olivedrab")
        plt.scatter(x, temp["pchs"].iloc[-offset:], alpha=0.9, c=np.int8((temp["pchs"] >= 0).values), cmap="PRGn",
                    label="pchdot", marker="*")
        now = datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        savename =  tittle+"_" +  now.strftime('%Y-%m-%d-%H-%M-%S')
        plt.title(cur_time + "\n" + data.index[-1], fontdict={'weight': 'normal', 'size': 40})


        # temp.to_csv(os.path.join(path, f"{savename}.csv"))
        # img = os.path.join(path, f"{tittle}.csv")
        # temp.to_csv(os.path.join(path, f"{tittle}.csv"))

        # WARNING
        warn = {}
        step1 = votes[-1] - votes[-2]
        step2 = votes[-2] - votes[-3]
        step_pch = pchs[-1] = pchs[-2]
        max5 = max(votes[-3:])
        min5 = min(votes[-3:])
        diff5 = max5 - min5
        """
        1.step 0.8
        2.5 max min diff 1
        3.continous 4
        4.vote cross
        5.pch cross 0+ 0- 
        5. max(diff/step)>0.8
        """
        ischange = False
        mv = np.mean(votes[-4:])
        for c in range(len(votes) - 2, -1, -1):
            if votes[-1] == 0:
                break
            if votes[c] * votes[-1] < 0:
                break
        continous_counter = len(votes) - c - 1
        stepw = step1 / totalvotes
        stepw2 = step2 / totalvotes

        temp["diff_vote"] = temp["votes"] - temp["votes"].shift(1)
        for cc in range(len(votes) - 2, -1, -1):
            if temp["diff_vote"].iloc[-1] == 0:
                break
            if temp["diff_vote"][cc] * temp["diff_vote"].iloc[-1] < 0:
                break

        # 同号votediff均值
        tend = temp["diff_vote"].iloc[cc + 1:].mean()
        tend_counter = len(votes) - cc - 1

        # 单调sum
        if tend_counter > 2 or (temp["diff_vote"].iloc[cc + 1:].sum() / totalvotes) > 0.99:
            warn["tend_counter"] = tend_counter
        warn["tend_sum"] = (temp["diff_vote"].iloc[cc + 1:].sum() / totalvotes)

        if (diff5) / totalvotes >= 1:
            warn["diff"] = (diff5) / totalvotes
        if continous_counter >= 100:
            warn["continous"] = continous_counter
            # warn["describe"] = ",".join(votes[c:])
        if (votes[-1] * votes[-2] < 0) and abs(stepw) > 0.3:
            warn["vote_cross"] = True
        if (pchs[-1] * pchs[-2] < 0):
            warn["pch_cross"] = True
        # if warn:

        warn.update({"name": tittle, "time": data.index[-1], "diff": (diff5) / totalvotes,
                     "continous": continous_counter, "tend": tend > 0})
        warn["tend_counter"] = tend_counter
        warn["tend_sum"] = round(abs(temp["diff_vote"].iloc[cc + 1:].sum()) / totalvotes, 1)
        # warn["index"] = round(abs(warn["tend_sum"]) / warn["tend_counter"],2)
        warn["index"] = votes[-1]
        warn["vote_step"] = step1  # round(stepw, 2)
        warn["pch_step"] = step_pch
        warn["step"] = stepw
        warn["diff"] = round((diff5) / totalvotes, 2)
        warn["step_2"] = max(abs(stepw2), abs(stepw))
        # if abs(stepw) >= 0.8 or (diff5) / totalvotes >= 1 or warn.get("pch_cross",False) or warn.get("vote_cross",False) or tend_counter>4 or warn.get("tend_sum")or (abs(votes[-1])>=14 and abs(step1)>5):
        # if (warn.get("vote_cross", False) or warn.get("vote_cross", False)) and (
        #         abs(stepw) >= 0.8 or (diff5 / totalvotes) >= 1.5):
        #     warn[
        #         "describe"] = f"vote_cross,{warn.get('vote_cross', False)}-step0.8,{abs(stepw) >= 0.8}-diff,{(diff5 / totalvotes) >= 1}"
        #     WARNING.append(warn)
        condiction = {}
        condiction["to_the_top"] = abs(votes[-1]) == totalvotes and abs(stepw) >= 0.8
        condiction["stepy_than_one"] = warn["step_2"] > 1
        condiction["continous_top"] = bool(abs(votes[-1]) == totalvotes and abs(warn.get("tend_sum")) >= 1.4)
        condiction["block_crash_step"] = bool(
            abs(actual_block_return[-1]) > 9 and max(abs(stepw2), abs(stepw)) > 0.8 and \
            actual_block_return[-1] * max(abs(stepw2), abs(stepw)) < 0)
        condiction["block_crash_pch"] = bool(abs(actual_block_return[-1]) > 9 and abs(actual_pch[-1]) > 1.9 and \
                                             actual_block_return[-1] * actual_pch[-1] < 0)
        step1_pch_diff = pchs[-1] * pchs[-2]
        last2 = temp["pchs"].iloc[-3:].values
        # print(f"last two {last2}")
        iscross01 = bool((last2[0] * last2[1] <= 0) and (last2[0] != 0))
        iscross12 = bool((last2[1] * last2[2] <= 0) and (last2[0] != 0))
        iscross02 = bool((last2[0] * last2[2] <= 0))

        cross_pch = np.mean(pchs[-3:])
        step1_pch = pchs[-1]
        condiction["sum3_pch"] = round(sum(pchs[-3:]), 2)
        # condiction["cross_pch"] = iscross02  # iscross01  # or iscross12 or iscross02
        # condiction["tend"] = bool((last2[-1] - last2[-2]) > 0)
        condiction["block_return"] = actual_block_return[-1]

        condiction["describe"] = ",".join([k if v else "" for k, v in condiction.items()])
        # condiction["test"] = True
        # for k, v in condiction.items():
        #     if k == "describe":
        #         continue
        #     if v:
        #         warn.update(condiction)
        #         WARNING.append(warn)
        #         break
        step1_pc = bool(abs(actual_pch[-1]) > 4.5)
        c3 = (actual_pch[-2] * actual_pch[-3]) > 0 and (actual_pch[-3] * actual_pch[-4]) > 0
        temp["pch_diff"] = temp["pchs"] - temp["pchs"].shift(1)
        # condiction["tend"] = bool((last2[1] - last2[0])>0)
        # condiction["tend"] = bool(round(temp["pch_diff"].iloc[-2:].sum()) > 0)

        condiction["index"] = round(abs(temp["pch_diff"].iloc[-3:].sum()), 2)
        condiction["step1_pc_gt_4.5"] = step1_pc
        condiction["continous_3"] = bool(
            c3 and actual_pch[-1] * c3 < 0 and abs(pc[-1]) > 0.015 and sum(pc[-4:-1]) > 0.06)
        if condiction["continous_3"]:
            condiction["describe"] += " 3 step continous decline"
        if step1_pc:
            condiction["describe"] += ", step -1 gt 4.5"
        condiction["describe"] += f"({round(last2[0], 2)}||{round(last2[1], 2)}||{round(last2[2], 2)})"
        condiction["cur_time"] = now.strftime('%Y-%m-%d %H:%M:%S')
        # datetime.now().strftime()
        diff_ = temp["pch_diff"].iloc[-2:].values

        sumresult = round(sum(diff_), 2)

        # condiction["cross_pch"] = (diff_[0]*diff_[1])

        v1 = smoothma[-2:]
        v1 = np.round(v1, 2)
        v11 = v1[-1] - v1[0]

        v2 = scale_close[-2:]
        v2 = np.round(v2, 2)
        v22 = v2[-1] - v2[0]

        condiction["index"] = np.round(v11 * v22, 3)
        #
        iscrossv = bool((v1[0] - v2[0]) * (v1[1] - v2[1]) <= 0)

        sy = re.findall("\d+X\d+", name)[0]

        # cosin = np.round(cosine_similarity(np.array([1, v11]).reshape([1, -1]), np.array([1, v22]).reshape([1, -1])), 3)
        s1 = pd.Series(smoothma)
        s11 = s1 - s1.shift(1).fillna(0)
        contiouse3 = all(map(lambda x: x >= 0, s11[-3:])) or all(map(lambda x: x <= 0, s11[-3:]))
        partialoffuture = round(abs(v2[-1] - v1[-1]) / ((abs(v11) + abs(v22)) / 2), 3)

        # condiction["cosin"] = cosin[0][0]
        condiction["cosin"] = 0
        condiction["contiouse3"] = contiouse3
        condiction["partialoffuture"] = partialoffuture
        # condiction["prewarn"] = all([cosin[0][0] < -0.15, contiouse3, partialoffuture < 1])
        # condiction["prewarn"] = all([cosin[0][0] < -0.15, contiouse3, partialoffuture < 1])

        cross_smooth = bool(smoothmadiff[-1] * smoothmadiff[-2] <= 0)
        tend_smooth = bool(smoothmadiff[-1] > 0)
        if sy in config["cross_pch"]:
            condiction["tend"] = bool(diff_[-1] > 0)
            condiction["cross_pch"] = iscross12
        elif sy in config["cross_vct"]:
            condiction["cross_pch"] = cross_smooth
            condiction["tend"] = tend_smooth
        elif sy in config["overlap"]:
            condiction["cross_pch"] = iscrossv
            condiction["tend"] = bool(v2[-1] > v1[-1])


        for i in range(1,30):
            tc = st[-(i+1)] * st[-i]
            if tc < 0:
                break

        savepath = os.path.join(path, f"{savename + '_' + str(condiction['tend']) + '_' + str(i)}.jpg")
        # if "DOGE30X1"  in savepath:
        #     print("fuck")
        warn["img"] = savepath
        if condiction["cross_pch"] or condiction.get("prewarn"):
            # if condiction["cross_pch"]:
            warn.update(condiction)

            cur = WARNING.get(name)
            cur.append(warn)
            try:
                if (len(cur) == 1 and not cur[0].get("email", False)) or \
                        (len(cur) > 1 and (cur[-2].get("tend") != cur[-1].get("tend")) and not cur[-1].get("email",False)):

                    warn["email"]  = True
                    cur[-1] = warn
                    # tt["email"] = True
                    # cur[-1] = tt
                    print(f"add emai {name}")
                    warns.append(warn)
                    # loop.run_in_executor(None, insert_warn, cur[-1])
            except Exception as e:
                print(repr(e), name)
            tt = {}
            tt["name"] = warn["name"]
            tt["time"] = warn["time"]
            tt["img"] = warn["img"]
            tt["cross_pch"] = warn["cross_pch"]
            tt["email"] = warn.get("email")
            tt["prewarn"] = warn.get("prewarn")
            tt["tend"] = warn.get("tend")
            tt["cur_time"] = warn.get("cur_time")
            cur[-1] = tt
            WARNING[name] = cur

        email = []
        for item in cur:
            if item.get("email"):
                email.append([item["time"], item["tend"]])
        datelist = data.index.tolist()
        indexofemail = []
        deltaf = lambda x: int(x[0]) * int(x[1])
        deltatime = deltaf(delta.split("X"))
        total = datetime.strptime(datelist[-1], "%Y-%m-%d %H:%M:%S") - datetime.strptime(datelist[0],
                                                                                         "%Y-%m-%d %H:%M:%S")
        l = len(datelist) - 1
        if  DEBUG  in savepath:
            print("fuck")


        for e in email:
            try:
                indexofemail.append([datelist.index(e[0]), e[0], e[1]])
                # m = datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S").minute
                # resiual = m % deltatime
            except:
                c = datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(datelist[0], "%Y-%m-%d %H:%M:%S")
                indexofemail.append([round((c / total) * l, 3), e[0], e[1]])
                pass
        for ee in indexofemail:
            if ee[0] <0:
                continue
            shifttime = (datetime.strptime(ee[1], "%Y-%m-%d %H:%M:%S") + dt.timedelta(seconds=deltatime * 60)).strftime(
                "%Y-%m-%d %H:%M:%S")
            plt.vlines(ee[0], -pscale * 0.6, pscale * 0.6, lw=5, color="green" if ee[-1] else "red", alpha=0.3)
            plt.text(ee[0] - 2, y=-pscale * 0.7, s=shifttime, alpha=1, fontsize=10,
                     color="k",
                     style="italic", weight="light", rotation=45)



        plt.legend(loc='upper left',
                   title=f"steps:{condiction['partialoffuture']}\n"
                         f"title:{tittle} \n"
                         f"prewarn:{condiction.get('prewarn')}\n"
                         f"SIMILARITY:{condiction['cosin']}\nindex {condiction['index']}\n"
                         f"SMOOTH {'|'.join([str(x) for x in v1])} \n"
                         f"SMOOTHDIFF {round(smoothmadiff[-2],3)}|{round(smoothmadiff[-1],3)} \n"
                         f"CLOSE {'|'.join([str(x) for x in v2])} \n"
                         f"average({round(last2[0], 2)}||{round(last2[1], 2)}||{round(last2[2], 2)})\n"
                         f"tend({condiction['tend']}||{sumresult})\n"
                         f"tend step:{i}\n"
                         f"diff({round(diff_[0], 2)}||{round(diff_[1], 2)})\n"
                         f"cross({condiction['cross_pch']})\n"
                         f"lasttime:{datelist[-1]} \n",
                   # f"last index {[ee[0]]}\n"
                   # f"lastw:{e[0]}",
                   fontsize=22, title_fontsize=22)


        print(f"save {savepath}")
        plt.savefig(savepath, bbox_inches='tight')
        plt.close()
        loop.run_in_executor(None, insert_warn, warn)
    print(f"process complete",crypts,se)
    if warns:
        loop.run_in_executor(None, httppost, warns)
        loop.run_in_executor(None, send, warns)
    # loop.run_in_executor(None, persist, WARNING)

def analysis(d):
    global first
    now = datetime.now()
    for deltaT, crypts in config["simple"].items():

        if first > len(config["simple"].keys()) and (now.minute % int(deltaT)) > 3:
            continue

        select = config["synth"].get(deltaT)
        if first > len(config["simple"].keys()) and int(deltaT) >=30:
            minute0 = (now - datetime(now.year, now.month, now.day)).seconds / 60
            select = list(filter(lambda x: (minute0 % (int(x.split("X")[0]) * int(x.split("X")[1]))) < 4, select))
        # hour0 = datetime(now.year, now.month, now.day)

        quantity = len(select) * len(crypts)
        cores = (quantity // 10) +1
        tasks = np.array_split(crypts,cores)
        first += 1
        with concurrent.futures.ProcessPoolExecutor() as pool:
            for j in tasks:
                loop.run_in_executor(pool, draw,select,j,d)

from datetime import datetime
import datetime as dt
less = 15
import asyncio

interval = 5
offset = 1
secondoffset = 12
async def main(d):
    while True:
        now = datetime.now()
        resiual = now.minute % interval
        start = time.time()
        analysis(d)
        delta = time.time() - start
        print(f"#######startAt {now} process cost {delta}")
        stime = abs(interval - resiual + offset)
        ws = stime * 60 - now.second - delta + secondoffset
        cur = datetime.now()
        nexttime = cur + dt.timedelta(seconds=ws)
        # print(f"#######current {datetime.now()} next time {stime} minute - {now.second} - {delta} + {secondoffset}")
        print(f"#######current {datetime.now()} next time {nexttime}")
        loop.run_in_executor(None, persist, d)
        await asyncio.sleep(ws)

if __name__ == '__main__':
    mgr = multiprocessing.Manager()
    d = mgr.dict()
    try:
        print("load warns")
        with open(os.path.join(datadir,warndir), "r") as f:
            WARNING = json.load(f)
        for k,v in WARNING.items():
            d[k] = v
    except:
        pass
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(d))