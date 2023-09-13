import numpy as np
import pandas as pd
from sklearn.linear_model import (
    LinearRegression, TheilSenRegressor, RANSACRegressor, HuberRegressor)
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sympy import *
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt

df = pd.read_csv("data/XRP/XRP_60.csv", index_col=0)
df.reset_index(drop=True)
df.set_index(["date"], inplace=True)
pd.set_option('mode.chained_assignment','warn')
# link = df[-400:]
link = df[-350:]
win = 18
m = 3
for i in range(m,win):
    link[i] = link["close"].rolling(i).mean().fillna(0).copy()
link = link[win:]
# link["close"].plot()

degree = 6
model = make_pipeline(PolynomialFeatures(degree), Ridge())
x = np.array(list(range(link.shape[0]))).reshape([-1,1])

for i in range(m, win):
    # model.fit(x,link[i].values.reshape([-1,1]))
    # print(model.steps[-1][-1].coef_)
    # f = lambda x:np.dot(np.round(model.steps[-1][-1].coef_,5),np.array([1,x,x**2,x**3,x**4,x**5]))[0] + np.round(model.steps[-1][-1].intercept_,3)[0]
    # xx = symbols("xx")
    # derf = lambdify(xx, diff(f(xx),xx), "numpy")
    # plt.plot(list(map(f,x)),c="red")
    # prey = model.predict(x)
    plt.scatter(x, link["close"], color='yellowgreen',label="training data")
    # plt.plot(prey,c="red",label="predict")
    plt.plot(link[i].values,label="ma"+str(i))
    der = link[i] - link[i].shift(1)
    offset = link[i][0] * 0.8
    plt.scatter(x,der.values*10 + offset,label="derivation",c=der>0)
    plt.axhline(y=offset, color='palevioletred', linestyle='-')
    plt.savefig(f"analysis/{'ma'+str(i)}.jpg")
    plt.legend(loc='upper left')
    plt.title('ma'+str(i))
    plt.show()
    plt.cla()
