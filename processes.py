import multiprocessing

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import sys

import numpy as np
import threading
import time
from random import randint
from threading import Thread
from multiprocessing import Process, Queue
import pickle

resenje = []
n = 4
steps = 2

deljenaMatrica = np.zeros((n, n), dtype="i")
"""deljenaMatrica.itemset((2, 3), 1)
deljenaMatrica.itemset((3, 4), 1)
deljenaMatrica.itemset((4, 2), 1)
deljenaMatrica.itemset((4, 3), 1)
deljenaMatrica.itemset((4, 4), 1)
deljenaMatrica.itemset((9, 10), 1)
deljenaMatrica.itemset((10, 10), 1)
deljenaMatrica.itemset((11, 10), 1)"""
deljenaMatrica[0][1] = 1
deljenaMatrica[1][1] = 1
deljenaMatrica[2][1] = 1

resenje.append(deljenaMatrica.astype(np.int8))

matrc = np.zeros((n, n), dtype="i")
for s in range(steps - 1):
    resenje.append(matrc.copy())

potezi = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
brojCelija = n * n

glavniRed = multiprocessing.Queue()

redovi = np.full((n, n), multiprocessing.Queue())
for i in range(n):
    for j in range(n):
        redovi[i][j] = multiprocessing.Queue()

class Celija(Process):
    global potezi
    global n
    global steps
    global resenje
    global redovi
    global deljenaMatrica
    global glavniRed
    novaVrednost = 0
    trenutnaVrednost = 0
    zivihSuseda = 0
    xx = 0
    yy = 0
    counter = 0

    def __init__(self, x, y, iteracija, value):
        Process.__init__(self)
        self.x = x
        self.y = y
        self.iteracija = iteracija
        self.value = value


    def run(self):
        for step in range(steps):
            self.zivihSuseda = 0

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

                poruka = (self.x, self.y, self.iteracija, self.value)
                serijalizovan = pickle.dumps(poruka)
                redovi[self.xx][self.yy].put(poruka)

            while True:
                if not redovi[self.x][self.y].empty():
                    primljeno = redovi[self.x][self.y].get()
                    primIter = primljeno[2]
                    primVrednost = primljeno[3]
                    if primIter == self.iteracija:
                        self.zivihSuseda += primVrednost
                        self.counter += 1

                        if self.counter == 8:
                            if self.zivihSuseda < 2:
                                self.novaVrednost = 0
                            elif self.zivihSuseda > 3:
                                self.novaVrednost = 0
                            elif (self.value == 1) and (self.zivihSuseda == 2 or self.zivihSuseda == 3):
                                self.novaVrednost = 1
                            elif (not (self.value == 1)) and self.zivihSuseda == 3:
                                self.novaVrednost = 1

                            self.value = self.novaVrednost
                            poruka = (self.x, self.y, self.iteracija, self.value)

                            glavniRed.put(poruka)
                            self.iteracija += 1
                            self.counter = 0

                            break
                        else:
                            redovi[self.x][self.y].put(primljeno)


def createMatrixArray():
    iter = 0
    brElemenataUIteraciji = dict()
    for i in range(steps):
        brElemenataUITeraciji[i] = 0
    while iter < steps:
        if not glavniRed.empty():
            primljeno = glavniRed.get()
            primX = primljeno[0]
            primY = primljeno[1]
            primIter = primljeno[2]
            primVrednost = primljeno[3]

            resenje[primIter][primX][primY] = primVrednost
            brElemenataUIteraciji[primIter] = brElemenataUITeraciji.get(primIter) + 1
            if brElemenataUITeraciji.get(primIter) == 8:
                iter += 1

listaProcesa = []

for i in range(n):
    for j in range(n):
        cell = Celija(i, j, 0, deljenaMatrica[i][j])
        listaProcesa.append(cell)

servisniProces = multiprocessing.Process(target = createMatrixArray)
servisniProces.start()

for index, proces in enumerate(listaProcesa):
    proces.start()

for proces in listaProcesa:
    proces.join()

servisniProces.join()

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
                         frames=len(steps), interval=100, blit=True, repeat=False);
    return anim


steps = resenje
anim = animate(steps);
HTML(anim.to_html5_video())