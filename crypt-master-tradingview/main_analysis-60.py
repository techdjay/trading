# from core.modeling import analysis
from core.modeling60minSmooth3 import analysis
import time
from core.configure import config
from datetime import datetime
import datetime as dt
less = 15
import asyncio

interval = 5
offset = 1
secondoffset = 0
async def main():
    while True:
        now = datetime.now()
        resiual = now.minute % interval
        start = time.time()
        analysis()
        delta = time.time() - start
        print(f"#######startAt {now} process cost {delta}")
        stime = abs(interval - resiual + offset)
        ws = stime * 60 - now.second - delta + secondoffset
        cur = datetime.now()
        nexttime = cur + dt.timedelta(seconds=ws)
        # print(f"#######current {datetime.now()} next time {stime} minute - {now.second} - {delta} + {secondoffset}")
        print(f"#######current {datetime.now()} next time {nexttime}")
        await asyncio.sleep(ws)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
