import matplotlib.pyplot as plt
import numpy as np

n = 6

x = [m for m in range(1,n+1)]
y = [np.sin(i) for i in x]

plt.plot(x, y)
plt.title("Berechnungszeitdiagramm für die Funktion")
# plt.xlim(1,n)
plt.xticks([1,3,6],list("aaa"))
# plt.xticks([i for i in range(1,n+1,8)])
plt.xlabel("n")
# plt.ylim(0,np.max(vector)+1)
plt.ylabel("Berechnungszeit (in ns)")
plt.grid()
plt.show()