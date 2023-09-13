import json
a = {"a":45}
with open("data.json","w") as f:

    json.dump(a,f)