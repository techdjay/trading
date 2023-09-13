import asyncio
import concurrent
import threading
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
    time.sleep(0.8)
    q.put(1000)
    return f"{i}fuck"



def done(par):
    q.put(898989)
    print("fucked:"+par.result() + "  ", q.queue)


loop = asyncio.get_event_loop()
# future = asyncio.ensure_future(main())
# future.add_done_callback(done)
# loop.run_until_complete(future)

# with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#     list(map(q.put, range(2, 10)))
#     while q:
#         try:
#             i = q.get_nowait()
#             if len(q.queue) <= 2 :
#                 break
#             print(q.queue)
#             f2 = loop.run_in_executor(executor,main3,i)
#             time.sleep(1)
#             # loop.call_soon_threadsafe(done)
#             f2.add_done_callback(done)
#         except:
#             break
futures = {}
def main(q):
    list(map(q.put, range(2, 10)))
    while q:
        try:
            i = q.get_nowait()
            if len(q.queue) <= 2 :
                break
            print(q.queue)
            f2 = loop.run_in_executor(None,main3,i)
            futures[i] = f2
            time.sleep(0.5)
            # loop.call_soon_threadsafe(f2.cancel)
            f2.add_done_callback(done)
        except:
            break


threading.Thread(target=main,args=(q,)).start()
# f2 = loop.run_in_executor(None,main2)
# f2.add_done_callback(done)
print("fcuk")
loop.run_forever()
# print("wait")
# time.sleep(5)


