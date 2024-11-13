import threading
import time

def affiche(n):
    for i in range(1, 6):
        print(i,": je suis le thread", n)
        time.sleep(1)


t1 = threading.Thread(target=affiche, args=(1,))
t2 = threading.Thread(target=affiche, args=(2,))

t1.start()
t2.start()

t1.join()
t2.join()