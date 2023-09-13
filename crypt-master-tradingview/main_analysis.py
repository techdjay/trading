# from core.modeling import analysis
from core.modelingplot import analysis
import time
from core.configure import config
from datetime import datetime
less = 5
import asyncio
async def main():
    while True:
        analysis()
        if datetime.now().minute % less != 0:
            resiual = datetime.now().minute % less
            print(f"current {datetime.now()} next time {less - resiual} minute")
            await asyncio.sleep((less - resiual) * 60)
        else:
            print(f"current {datetime.now()} next time {less} minute")
            await asyncio.sleep(60 * less)
        await asyncio.sleep(0.001)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())