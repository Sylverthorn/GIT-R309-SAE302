import threading
import time

def count(n, thread):
    for i in range(n, 0):
        print(f"Thread {thread} : {i}")
        time.sleep(1)


t1 = threading.Thread(target=count, args=(5, 1))
t2 = threading.Thread(target=count, args=(20, 2))

t1.start()
t2.start()

t2.join()
t1.join()