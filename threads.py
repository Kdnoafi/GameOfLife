from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import sys

import numpy as np
import threading
import time
from random import randint
from threading import Thread

resenje = []
n = 17
steps = 50

deljenaMatrica = np.zeros((n, n), dtype="i")
deljenaMatrica.itemset((2, 3), 1)
deljenaMatrica.itemset((3, 4), 1)
deljenaMatrica.itemset((4, 2), 1)
deljenaMatrica.itemset((4, 3), 1)
deljenaMatrica.itemset((4, 4), 1)
deljenaMatrica.itemset((9, 10), 1)
deljenaMatrica.itemset((10, 10), 1)
deljenaMatrica.itemset((11, 10), 1)

resenje.append(deljenaMatrica.astype(np.int8))

potezi = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

howManyReadMeMatrica = np.zeros((n, n), dtype="i")
maxReadMe = 8
brojCelija = n * n
brojacPredIteraciju = 0

deljenaLock = threading.Lock()
lock8 = threading.Lock()
globalBrojacLock = threading.Lock()

semafori = np.full((n, n), threading.Semaphore(0))
for i in range(n):
    for j in range(n):
        semafori[i][j] = threading.Semaphore(0)

condition = threading.Condition()


class Celija(Thread):
    global globalBrojacLock
    global potezi
    global n
    global steps
    global resenje
    global lock8
    global deljenaLock
    global semafori
    global howManyReadMeMatrica
    global maxReadMe
    global deljenaMatrica
    global brojCelija
    global brojacPredIteraciju
    global condition
    iteracija = 0
    novaVrednost = 0
    trenutnaVrednost = 0
    zivihSuseda = 0
    xx = 0
    yy = 0

    def __init__(self, x, y):
        Thread.__init__(self)
        self.x = x
        self.y = y

    def run(self):
        global brojacPredIteraciju
        for step in range(steps):
            self.zivihSuseda = 0
            deljenaLock.acquire()
            self.trenutnaVrednost = deljenaMatrica[self.x][self.y]
            deljenaLock.release()

            for k in range(8):
                self.xx = self.x + potezi[k][0]
                self.yy = self.y + potezi[k][1]
                if self.xx >= n:
                    self.xx = 0
                elif self.xx < 0:
                    self.xx = n - 1
                if self.yy >= n:
                    self.yy = 0
                elif self.yy < 0:
                    self.yy = n - 1

                deljenaLock.acquire()  # ||LOCK||
                self.zivihSuseda += deljenaMatrica[self.xx][self.yy]
                deljenaLock.release()  # ||LOCK||

                lock8.acquire()  # ||LOCK||
                howManyReadMeMatrica[self.xx][self.yy] += 1
                if howManyReadMeMatrica[self.xx][self.yy] == maxReadMe:
                    semafori[self.xx][self.yy].release()
                lock8.release()  # ||LOCK||

            if self.zivihSuseda < 2:
                self.novaVrednost = 0
            elif self.zivihSuseda > 3:
                self.novaVrednost = 0
            elif (self.trenutnaVrednost == 1) and (self.zivihSuseda == 2 or self.zivihSuseda == 3):
                self.novaVrednost = 1
            elif (not (self.trenutnaVrednost == 1)) and self.zivihSuseda == 3:
                self.novaVrednost = 1

            semafori[self.x][self.y].acquire()

            deljenaLock.acquire()  # ||LOCK||
            deljenaMatrica[self.x][self.y] = self.novaVrednost
            deljenaLock.release()  # ||LOCK||

            condition.acquire()
            globalBrojacLock.acquire()  # ||LOCK||
            brojacPredIteraciju += 1;
            globalBrojacLock.release()  # ||LOCK||
            if brojacPredIteraciju < brojCelija:
                condition.wait()
            self.iteracija += 1
            condition.release()
            if brojacPredIteraciju == brojCelija:
                condition.acquire()
                condition.notifyAll()
                resenje.append(deljenaMatrica.copy())
                howManyReadMeMatrica.fill(0)
                brojacPredIteraciju = 0
                condition.release()


listaThreadova = []

for i in range(n):
    for j in range(n):
        listaThreadova.append(Celija(i, j))

for index, nit in enumerate(listaThreadova):
    nit.start()

for nit in listaThreadova:
    nit.join()

print(deljenaMatrica)
print(len(resenje))

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np


def animate(steps):

    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True);

    anim = FuncAnimation(im.get_figure(), animate, init_func=init,
                         frames=len(steps), interval=500, blit=True, repeat=False);
    return anim


steps = resenje
anim = animate(steps);
HTML(anim.to_html5_video())