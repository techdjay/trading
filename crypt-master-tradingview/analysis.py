import matplotlib.pyplot as plt
import pandas as pd
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

files = glob.glob("data/LINK/LINK_60.csv")

df = pd.read_csv("data/LINK/LINK_60.csv", index_col=0)
df.reset_index(drop=True)
df.set_index(["date"], inplace=True)

fig = go.Figure()
pd.set_option('mode.chained_assignment','warn')
# link = df[-400:]
link = df[-100:]
link["pchange"] = np.round(((link["close"]-link["open"])/link["open"])*100,1)
win = 18
m = 2

for i in range(m,win):
    link[i] = link["close"].rolling(i).mean().fillna(0).copy()
    print(((i-5)/15)*150)
    fig.add_trace(go.Scatter(x=link.index[win:], y=link[i][win:],
                             mode='lines',
                             name="ma"+str(i),
                             marker_color=f'rgba({((i-m)/(win-m))*250}, 50, 0, .8)',
                             marker=dict(
                                 size=16,
                                 cmax=20,
                                 cmin=5,
                                 color=i
                             )
                             ))

link = link[i+1:]
fig.add_trace(go.Candlestick(x=link.index,
                             text=link["pchange"],
                             open=link['open'],
                             high=link['high'],
                             low=link['low'],
                             close=link['close']))

fig.update_layout(
    paper_bgcolor="lightgray",
    height=900,  # Added parameter
    width = 2000
)
fig.update_yaxes(automargin=True)
fig.show()
fig.write_image("analysis/fuck.png")
