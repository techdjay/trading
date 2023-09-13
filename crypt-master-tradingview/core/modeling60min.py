import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os
# from core.emailSender import send
from core.emailSender2 import send
from datetime import datetime
import asyncio
from core.DBUtils import insert_record, insert_warn
import json
import re
from core.blocksearch import bsearch
from matplotlib.collections import LineCollection
from core.configure import config

DATADIR = "data"
SAVEDIR = "blocks"
delta = "60"
win = 11
offset1 = -100
deltas = list(range(1, win))
deltas = [5, 6, 7, 8, 9, 10]
deltas = [5,6,7]
totalvotes = 3
loop = asyncio.get_event_loop()

def dataset(select=None, crypts=None):
    for files in glob(DATADIR + "/*"):
        for file in glob(files + "/*"):
            if select:
                for s in select:
                    if s in file:
                        break
                else:
                    continue
            if crypts:
                for c in crypts:
                    if c in file:
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

            df = df[20:]
            rows = df.shape[0]

            yield df, file.split(os.sep)[-1].split(".")[0], vote[-rows:], pch[-rows:], actual_pch[-rows:],ma[-rows:],pc[-rows:]





crypts = config["crypts"]
datadir = os.getcwd()
# WARNING={}
# with open(os.path.join(datadir,"WARNING.json"),"w+") as f:
#     WARNING = json.load(f)


def analysis():
    # gen = dataset(select=["30"],crypts = ["BCH","XRP"])
    gen = dataset(select=["60"], crypts=[ "ZEC", "BSV", "XRP","LINK","ETH"])
    # gen = dataset(select=["30"], crypts=crypts)
    global totalvotes
    temp = {}
    WARNING = []
    offset = 0
    for data, name, vote, pch, actual_pch,ma ,pc in gen:
        # if "DOGE" not in name:
        #     continue
        plt.figure(figsize=(46, 20))
        votes = []
        pchs = []
        mas = []
        for i in range(data.shape[0] - 1, -1, -1):
            # votes.insert(0, sum(vote.iloc[i, :]) - (win - sum(vote.iloc[i, :])))
            t = sum(vote.iloc[i, :])
            m = sum(ma.iloc[i,:])
            f = totalvotes - t
            votes.insert(0, t - f)
            pchs.insert(0, pch.iloc[i].mean())
            mas.insert(0,round(m/totalvotes,2))

        tittle = name
        x = list(range(data.shape[0]))

        cryp = re.match("[A-Z]*", name).group()
        delta = name.split(cryp)[-1]
        path = os.path.join(SAVEDIR, cryp, delta)
        os.makedirs(path, exist_ok=True)
        # plt.legend(loc='upper left', title=data.index[-1])

        temp = pd.DataFrame({"date": data.index, "votes": votes, "pchs": pchs,"mas":mas,"pc":pc})
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
        ax.add_collection(LineCollection(segments, colors=linecolors, lw=7, alpha=0.7))
        # plt.plot(result[:, 0], result[:, 1] > 0)
        # data["close"].plot()
        # plt.plot((data["close"] - data["close"].mean()) / 50)
        scale = data["close"].max() - data["close"].min()
        minclose = data["close"].min()
        pscale = max(pchs) - min(pchs)
        f = lambda x: pscale * (x - minclose) / scale - pscale / 2
        turnscale_f = lambda r: (pscale * r) / ((win - 1) * 2)

        scale_actual_pch = list(map(turnscale_f, actual_pch))
        # scale close and mean 6
        scale_close = list(map(f, data["close"]))
        plt.plot(scale_close, label="close", alpha=0.6)
        plt.scatter(x, scale_close, marker="d", alpha=0.6)
        # plt.plot(list(map(f, data[6])), label="ma6", alpha=0.6)
        plt.bar(x, scale_actual_pch, color=["lightgreen" if x > 0 else "cornflowerblue" for x in actual_pch[-offset:]],
                alpha=0.4)
        for i in deltas:
            plt.plot(list(map(f, ma[i])),label=f"ma{i}")
        # plt.plot(list(map(f,temp["mas"])), alpha=0.6, color="olive",label="ma")
        madiff = np.round(temp["mas"] - temp["mas"].shift(1),2)
        madiff.fillna(0,inplace=True)
        minma = temp["mas"].min()
        mascale = temp["mas"].max() - temp["mas"].min()
        fma = lambda x: pscale * (x - minma) / mascale - pscale / 2

        # plt.plot(madiff.values/10, alpha=0.59, color="indigo", label="madiff")
        # plt.plot(temp["turn"], label="turn")
        # plt.plot(list(map(turnscale_f, temp["turn"])), label="turn")
        scale_vote = list(map(turnscale_f, temp["votes"]))
        # plt.plot(scale_vote, label="votes", alpha=0.6)

        # plt.scatter(x, scale_vote, label="vote", marker="*", s=40, color="midnightblue")
        # plt.scatter(x, scale_vote, s=[abs(x + 1) ** 3 for x in votes[-offset:]],
        #             c=["lightgreen" if x > 0 else "cornflowerblue" for x in votes[-offset:]],
        #             alpha=0.8, label="vote")
        # vote
        # for i in range(len(x)):
        #     plt.text(x[i], scale_vote[i],
        #              votes[i], alpha=0.6, fontsize=10,
        #              color="indigo",
        #              style="italic", weight="light")
        for i in range(len(x)):
            plt.text(x[i], scale_actual_pch[i],
                     actual_pch[i], alpha=0.6, fontsize=10,
                     color="indigo",
                     style="italic", weight="light")
        # bound
        plt.scatter([blockx[xx] for xx in seg], [0] * len(seg), alpha=0.5, label="bound")

        # block return
        # for i in range(len(seg) - 1):
        #     plt.text(blockx[seg[i]] + len(segments[i]) / 2, -pscale*0.2,
        #              round(sum(pchs[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1]), 2), alpha=0.9, fontsize=10,
        #              color="indigo",
        #              style="italic", weight="light", rotation=45)
        # actual return
        actual_block_return = [round(sum(actual_pch[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1]), 2) for i in
                               range(len(seg) - 1)]

        for i in range(len(seg) - 1):
            plt.text(blockx[seg[i]] + len(segments[i]) / 2, -pscale * 0.2,
                     actual_block_return[i], alpha=0.9, fontsize=10,
                     color="indigo",
                     style="italic", weight="light", rotation=45)

        xticks = [blockx[xx] for xx in seg]
        plt.xticks([blockx[xx] for xx in seg], data.index[xticks], rotation=45, color="dimgrey")
        plt.plot(temp["pchs"].iloc[-offset:], alpha=0.6, label="pch", c="olivedrab")

        plt.plot(x, temp["pchs"].iloc[-offset:], alpha=0.6, color="tomato",label="pchdot", marker="*")

        # colors = ['teal', 'yellowgreen', 'gold']
        # offsett = -20
        # tx = np.array(x[:offsett]).reshape([-1,1])
        # ty = np.array(mas[:offsett]).reshape([-1,1])
        # testx = np.array(x[offsett:]).reshape([-1,1])
        # for count, degree in enumerate([3, 4, 5]):
        #     model = make_pipeline(PolynomialFeatures(degree), Ridge())
        #     model.fit(tx,ty)
        #     y_plot = model.predict(testx)
        #     plt.plot(testx, y_plot, color=colors[count], linewidth=3,
        #              label="degree %d" % degree)

        savename = f"{tittle}_{datetime.now().strftime('%Y%m-%d-%H-%M')}"
        plt.title(savename + "_" + data.index[-1], fontdict={'weight': 'normal', 'size': 40})

        plt.legend(loc='upper left', title=data.index[-1])
        # plt.axhline(y=0, color='palevioletred', linestyle='-')
        # plt.plot(result[:,2])
        # temp["date"] = data["date"]
        savepath = os.path.join(path, f"{savename}.jpg")
        print(f"save {savepath}")
        temp.to_csv(os.path.join(path, f"{savename}.csv"))
        # img = os.path.join(path, f"{tittle}.csv")
        # temp.to_csv(os.path.join(path, f"{tittle}.csv"))
        plt.savefig(savepath, bbox_inches='tight')
        # plt.show()
        # break
        plt.close()
        # plt.cla()

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
        warn.update({"name": tittle, "time": data.index[-1], "img": savepath, "diff": (diff5) / totalvotes,
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
        condiction["continous_top"] = abs(votes[-1]) == totalvotes and abs(warn.get("tend_sum")) >= 1.4
        condiction["block_crash_step"] = abs(actual_block_return[-1]) > 9 and max(abs(stepw2), abs(stepw)) > 0.8 and \
                                         actual_block_return[-1] * max(abs(stepw2), abs(stepw)) < 0
        condiction["block_crash_pch"] = abs(actual_block_return[-1]) > 9 and abs(actual_pch[-1]) > 1.9 and \
                                        actual_block_return[-1] * actual_pch[-1] < 0
        step1_pch_diff = pchs[-1]* pchs[-2]
        last2 = temp["pchs"].iloc[-2:].values
        print(f"last two {last2}")
        iscross = (last2[0] * last2[1] <= 0) and (last2[0] != 0)
        cross_pch = np.mean(pchs[-3:])
        step1_pch = pchs[-1]
        condiction["sum3_pch"] = round(sum(pchs[-3:]),2)
        condiction["cross_pch"] = iscross
        condiction["tend"] = (last2[1] - last2[0]) > 0
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
        step1_pc = abs(actual_pch[-1])  > 4.5
        c3 = (actual_pch[-2] *actual_pch[-3]) >0 and (actual_pch[-3]* actual_pch[-4]) > 0
        condiction["step1_pc_gt_4.5"] =step1_pc
        condiction["continous_3"] = c3 and actual_pch[-1]*c3 <0 and abs(pc[-1])>0.015 and sum(pc[-4:-1]) >0.06
        if condiction["continous_3"]:
            condiction["describe"] += " 3 step continous decline"
        if step1_pc:
            condiction["describe"] += ", step -1 gt 4.5"

        if condiction["cross_pch"]:
            warn.update(condiction)
            WARNING.append(warn)
        loop.run_in_executor(None, insert_warn, warn)

    if WARNING:
        send(WARNING)
