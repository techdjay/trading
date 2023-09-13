
import asyncio
import concurrent
import os
import time

loop = asyncio.get_event_loop()

def fuck():
    i = 0
    try:
        while i<10:
            i+=1
        print(i)
        raise Exception("fuck")
    except Exception as e:
        return e

def mycallback(future):
    print("callback",future.result())

def task():
    print(f"pid {os.getpid()}")
    future = loop.run_in_executor(None,fuck)
    future.add_done_callback(mycallback)
    # time.sleep(3)
    loop.run_until_complete(future)
    return "done task"

async def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
            # future = loop.run_in_executor(pool, task)
            future = executor.submit(task)
            future.add_done_callback(mycallback)

if __name__ == '__main__':
    print(f"main pid {os.getpid()}")
    loop.run_until_complete(main())