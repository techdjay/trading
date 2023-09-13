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
offset1 = -150
deltas = list(range(1, win))
deltas = [5, 6, 7, 8, 9, 10]
deltas = [10, 9, 11, 12]

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
            actual_pch = (df["close"] / df["close"].shift(1) - 1).values * 100
            actual_pch = np.round(actual_pch, 1)
            for i in deltas:
                df[i] = df["close"].rolling(i).mean().fillna(0).copy()
                pch[i] = (df[i] / df[i].shift(1) - 1).round(4) * 100
                vote[i] = (df[i] - df[i].shift(1)) > 0
            df = df[20:]
            rows = df.shape[0]

            yield df, file.split(os.sep)[-1].split(".")[0], vote[-rows:], pch[-rows:], actual_pch[-rows:]


def warn_local(imgs):
    os.makedirs(os.path.join("warn"), exist_ok=True)


crypts = config["crypts"]


def analysis():
    # gen = dataset(select=["30"],crypts = ["BCH","XRP"])
    gen = dataset(select=["15"], crypts=["DOGE", "ZEC", "BSV", "XRP"])
    # gen = dataset(select=["30"], crypts=crypts)
    temp = {}
    WARNING = []
    offset = 0
    for data, name, vote, pch, actual_pch in gen:
        # if "DOGE" not in name:
        #     continue
        plt.figure(figsize=(46, 20))
        votes = []
        pchs = []
        for i in range(data.shape[0] - 1, -1, -1):
            # votes.insert(0, sum(vote.iloc[i, :]) - (win - sum(vote.iloc[i, :])))
            t = sum(vote.iloc[i, :])
            f = win - 1 - t
            votes.insert(0, t - f)
            pchs.insert(0, round(pch.iloc[i].mean(),3))

        tittle = name
        x = list(range(data.shape[0]))

        cryp = re.match("[A-Z]*", name).group()
        delta = name.split(cryp)[-1]
        path = os.path.join(SAVEDIR, cryp, delta)
        os.makedirs(path, exist_ok=True)
        # plt.legend(loc='upper left', title=data.index[-1])

        temp = pd.DataFrame({"date": data.index, "votes": votes, "pchs": pchs})
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
        plt.ylim()
        pscale = max(pchs) - min(pchs)
        ylim = max(abs(max(pchs)),abs(min(pchs)))*1.1
        plt.ylim(-ylim,ylim)
        f = lambda x: pscale * (x - minclose) / scale - pscale / 2
        turnscale_f = lambda r: (pscale * r) / ((win - 1) * 2)

        scale_actual_pch = list(map(turnscale_f, actual_pch))
        # scale close and mean 6
        scale_close = list(map(f, data["close"]))
        plt.plot(scale_close, label="close", alpha=0.6)
        # plt.plot()
        plt.scatter(x, scale_close, marker="d", alpha=0.6)
        plt.plot(list(map(f, data[10])), label="ma10", alpha=0.6)
        plt.bar(x, scale_actual_pch, color=["lightgreen" if x > 0 else "cornflowerblue" for x in actual_pch[-offset:]],alpha=0.4)
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
        plt.scatter([blockx[xx] for xx in seg], [0] * len(seg),marker='>', label="bound")

        # block return
        # for i in range(len(seg) - 1):
        #     plt.text(blockx[seg[i]] + len(segments[i]) / 2, -pscale*0.2,
        #              round(sum(pchs[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1]), 2), alpha=0.9, fontsize=10,
        #              color="indigo",
        #              style="italic", weight="light", rotation=45)
        # actual return
        actual_block_return = [round(sum(actual_pch[seg[i] if i == 0 else seg[i] + 1:seg[i + 1] + 1]), 2) for i in
                               range(len(seg) - 1)]

        for i in range(len(seg)):
            plt.text(blockx[seg[i]] + len(segments[i]) / 2, -pscale * 0.2,
                     actual_block_return[i], alpha=0.9, fontsize=10,
                     color="indigo",
                     style="italic", weight="light", rotation=45)
            plt.axvline(blockx[seg[i]],-100,100,color="darkgrey",alpha=0.4)



        xticks = [blockx[xx] for xx in seg]
        plt.xticks([blockx[xx] for xx in seg], data.index[xticks], rotation=45, color="dimgrey")

        plt.plot(temp["pchs"], alpha=0.5, label="pch", c="olivedrab")
        plt.plot(x, temp["pchs"], alpha=0.5, label="pchdot", marker="^")
        perchange = temp["pchs"].values
        for i in range(len(x)):
            plt.text(x[i], perchange[i],
                     perchange[i], alpha=0.2, fontsize=10,
                     color="red",
                     style="italic", weight="light")

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
        totalvotes = win - 1
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

        step1_pch_diff = perchange[-1]* perchange[-2]
        cross_pch = np.mean(perchange[-3:])
        step1_pch = pchs[-1]
        condiction["sum3_pch"] = round(sum(perchange[-3:]),2)
        condiction["cross_pch"] = step1_pch_diff < 0
        condiction["tend"] = cross_pch > 0
        condiction["block_return"] = actual_block_return[-1]

        condiction["describe"] = str(round(perchange[-2],2)) + str(round(perchange[-1],2)) +  ",".join([k if v else "" for k, v in condiction.items()])
        # condiction["test"] = True
        # for k, v in condiction.items():
        #     if k == "describe":
        #         continue
        #     if v:
        #         warn.update(condiction)
        #         WARNING.append(warn)
        #         break
        warn.update(condiction)
        if condiction["cross_pch"]:
            WARNING.append(warn)
        loop.run_in_executor(None, insert_warn, warn)
    if WARNING:
        send(WARNING)
