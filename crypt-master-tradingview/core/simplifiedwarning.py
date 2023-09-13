import json
with open("WARNING.json") as f:

    data = json.load(f)

newdict = {}
for k,v in data.items():
    t = []
    for item in v:
        tt = {}
        tt["name"] = item["name"]
        tt["time"] = item["time"]
        tt["img"] = item["img"]
        tt["cross_pch"] = item["cross_pch"]
        tt["email"] = item.get("email")
        tt["prewarn"] = item.get("prewarn")
        tt["tend"] = item.get("tend")
        tt["cur_time"] = item.get("cur_time")
        t.append(tt)
    newdict[k] = t
with open("newdict.json","w") as f:
    json.dump(newdict,f)





