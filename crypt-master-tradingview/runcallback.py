import asyncio
import time




async def main():
    await asyncio.sleep(0.3)
    print("fuck")
    return "hello"


def main2():
    time.sleep(0.1)
    print("fuck")
    if 1:
        return "hello"
import queue

q = queue.Queue()

def main3(i):
    # if i ==3:
    print(f"fuck: {i}")
    time.sleep(0.01)
    # q.put(1000)
    return f"{i}fuck"
    time.sleep(3)
    return f"{i}hello"


def done(par):
    print("fucked:"+par.result())

loop = asyncio.get_event_loop()
# future = asyncio.ensure_future(main())
# future.add_done_callback(done)
# loop.run_until_complete(future)
list(map(q.put,range(2,10)))
while q:
    try:
        i = q.get_nowait()
        if len(q.queue) <= 2 :
            break
        print(q.queue)
        f2 = loop.run_in_executor(None,main3,i)
        time.sleep(1)
        f2.add_done_callback(done)
    except:
        break

# f2 = loop.run_in_executor(None,main2)
# f2.add_done_callback(done)
loop.run_forever()
# print("wait")
# time.sleep(5)


