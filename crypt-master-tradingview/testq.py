import queue

q = queue.Queue()

data = {"f1":"fuck1","f2":"fuck2"}

for k,v in data.items():
    q.put(k+v)

i = 0
while q:
    i+=1
    item = q.get_nowait()
    print(item)
    q.put(f"f3fuck3{i}")
    i+=1
print("end")