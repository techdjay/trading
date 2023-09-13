
import time
from core.configure import fuckdict
from fastapi import FastAPI
GLOBAL_VAR = "default"
fuck2 = {"a":1}


import uvicorn
app = FastAPI()

@app.get("/long")
def fakelongcall():
    cpt = 0
    while cpt < 30:
        print(fuckdict)
        print(fuck2)
        time.sleep(1)
        cpt = cpt + 1


@app.get("/short/{fuck}")
def fakeshortcall(fuck: str):
    global GLOBAL_VAR,fuckdict
    fuckdict["fuck"] = fuck
    fuck2["c"] = 3
    print("Change done !")

if __name__ == '__main__':
    fuck2["b"]  = 2
    fuckdict["fuckyou"] = "thity"
    uvicorn.run(app='fasttest:app', host="0.0.0.0", port=9300,workers=0, reload=False)
