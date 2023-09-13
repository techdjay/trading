# from core.modeling import analysis
from core.modelingultra import analysis
import time
from core.configure import config
from datetime import datetime
less = 15
import asyncio

interval =60
offset = 3
async def main():
    while True:
        resiual = datetime.now().minute % interval
        start = time.time()
        analysis()
        print(f"####### process cost {time.time() - start}")
        # print(f"####### process cost {time.time() - start}")
        stime = abs(interval - resiual + offset)
        print(f"current {datetime.now()} next time {stime} minute")
        await asyncio.sleep(stime * 60)
        await asyncio.sleep(0.001)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
