from core import configure
from core import DBUtils
import datetime as dt
from datetime import datetime
import pandas as pd


now = datetime.now()
para = {"delta":"%15X1","time":now-dt.timedelta(hours=40)}
result = DBUtils.get_warn_group(para)
print(result)

DBUtils.get_warn2(para)

df = pd.DataFrame(result,columns=["time","down","up"])
t = []
for i in range(1,df.shape[0]):
    item1 = df.iloc[i-1,:]
    item2 = df.iloc[i, :]
    delta = item2["time"] - item1["time"]
    if item2["up"] >=12 or item2["down"] >=12:
        t.append(item2)
    elif delta.seconds<= 15*60:
        if item1["up"] + item2["up"] >=13 and item1["up"] >=5 and item1["up"] < 10:
            item2["up"] = item2["up"] + item1["up"]
            t.append(item2)
        elif item1["down"] + item2["down"] >=13 and item1["down"] >=5  and item1["down"] < 10:
            item2["down"] = item2["down"] + item1["down"]
            t.append(item2)

print(df.describe())
df2 = pd.DataFrame(t)
print(df2.describe())