# from core.modeling import analysis
from core.modeling5min1 import analysis
# from core.modelingubantu21 import analysis
import time
from core.configure import config
from datetime import datetime
interval = 5
offset = 4
import asyncio
async def main():
    while True:
        resiual = datetime.now().minute % interval
        start = time.time()
        analysis()
        print(f"####### process cost {time.time() - start}")
        if resiual != offset:
            print(f"current {datetime.now()} next time {offset - resiual} minute")
            await asyncio.sleep((offset - resiual) * 60)
        else:
            print(f"current {datetime.now()} next time {interval} minute")
            await asyncio.sleep(60 * interval)
        await asyncio.sleep(0.001)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())