import pandas as pd


import numpy as np

arr = np.linspace(1,9,9).reshape([-1,3])
print(arr)
df = pd.DataFrame(arr,list("abc"))
print(df)

df[0]['b'] = 45
df.loc["a",0] = 65
item = df.iloc[2]

item[2] = item[1] + item[0]
print(df)
print(item)