import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os
from core.emailSender import send


DATADIR = "data"
SAVEDIR = "analysis"
delta = "60"
win = 18
m = 3
offset1 = -350
deltas = [1,5,10,13]
def dataset(select=None):
    for files in glob(DATADIR + "/*"):
        for file in glob(files + "/*"):
            if select:
                for s in select:
                    if s in file:
                        break
                else:
                    continue
            df = pd.read_csv(file,index_col=0)
            if df.empty or df.shape[0] < 100:
                print(f"empty {file} ")
                continue
            df.reset_index(drop=True)
            df.set_index(["date"], inplace=True)
            df = df[offset1:]
            for i in deltas:
                df[i] = df["close"].rolling(i).mean().fillna(0).copy()
            df = df[deltas[-1]:]
            yield df,file.split("\\")[-1].split(".")[0]

if __name__ == '__main__':
    gen = dataset(select=["15","30","60"])
    gen = dataset(select=["60"])
    package = {}
    for data,name in gen:
        x = np.array(list(range(data.shape[0]))).reshape([-1, 1])
        # for i in deltas:
        for i in [10]:
            plt.figure(figsize=(26, 13))
            tittle = name + '-MA-' + str(i)
            data.reset_index(inplace=True)
            data["redate"] = np.copy(data["date"].iloc[::-1])
            data["re"+str(i)] = np.copy(data[i].iloc[::-1])
            plt.scatter(x, data["close"], color='yellowgreen', label="training data")
            # plt.plot(prey,c="red",label="predict")
            plt.plot(data[i].values, label="ma" + str(i))
            der = data[i] - data[i].shift(1)
            offset = data[i][0] * 0.8
            plt.scatter(x, der.values * 10 + offset, label="derivation", c=der > 0)

            if "LINK" in name and "60" in name:
                print(name)
            temp = (der > 0).values[::-1]
            data["der"] = np.copy(der.values[::-1])
            data["reclose"] = np.copy(data["close"].iloc[::-1])
            for ix in range(temp.shape[0]-8):
                tx = temp[ix:ix + 5]
                if (sum(tx) == 4 and tx[2] == False) or (sum(tx) == 1 and tx[2] == True):
                    temp[ix+2] = not temp[ix+2]
            data["blocks"] = temp
            data["anchors"] = data["blocks"] == data["blocks"].shift(1)
            blocks = []
            t = []
            anchor = 0
            for index in data["anchors"][data["anchors"] == False].index:
                # data["low"][data["low"] == 0.55721].index
                # if  index-anchor<3:
                #     blocks.append([-1]*(index-anchor))
                blocks.append(data["blocks"].iloc[anchor:index].values)
                anchor = index
            plt.plot(der.values * 10 + offset,c="cyan",label="derivation")
            plt.axhline(y=offset, color='palevioletred', linestyle='-')
            path = os.path.join(SAVEDIR, name.split("_")[0])
            os.makedirs(path,exist_ok=True)
            plt.legend(loc='upper left',title=data.index[-1])
            plt.title(tittle)
            savepath = os.path.join(path, f"{tittle}.jpg")
            print(f"save {savepath}")
            plt.savefig(savepath,bbox_inches='tight')
            plt.show()
            plt.cla()

            # if len(blocks[1])>=3 and len(blocks[0]<3):

            package[name] = ["fuck",savepath]
    send(package)



















