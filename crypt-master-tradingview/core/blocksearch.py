import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def bsearch(arr, less, step):
    candidate = {}
    for i in range(arr.shape[0] - less-1, -1, -step):
        t = []
        bound = less
        while i - bound > 0 and i + bound < arr.shape[0]:
            t.append(np.sum(arr[i - bound:i + bound+1]))
            if len(t)>3 and all([t[-1]-t[-2]<0,t[-2]-t[-1]<0]):
                t = t[:-3]
                print("continum")
                break
            if len(t)>2 and (t[-1] /t[-2]) < 0.85:
                t = t[:-1]
                break
            bound += 1
        if not t:
            continue
        k = max(t)
        b = t.index(k) + less
        candidate[i] = (k,b)
    temp = []
    for anchor,(total,bound) in candidate.items():
        temp.append([anchor,total,bound])
    data = np.array(temp)
    return data
    # plt.plot(data[:,1])
    # plt.plot(data[:,2])
    # plt.show()


# df = pd.read_csv("bch.csv", index_col=0)
# df["data"] = np.abs(df["votes"]) * df["pchs"]
# print(df.shape)
# bsearch(df["data"].values.reshape([-1,1]),1,1)