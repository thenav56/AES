#!/usr/bin/python
#HARD MARGIN CLASSIFIER TEST
from math import *
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

def getclass(data, cls):
    return [(a, b) for (a, b) in data if b == cls]

def pl(c0, t):
        x = []
        y = []
        for a, _ in c0:
            x.append(a[0])
            y.append(a[1])
        plt.plot(x, y, t)

def cl(w, b, data):
    f = np.dot(w, data) - b
    return 1 if f >= 0 else -1

def drawline(w, b, col):
    #w[0] * x + w[1] * y + b = 0
    x = []
    y = []
    for i in range(-4, 4): #y
        x += -(b + w[1] * i) / w[0],
        y += i,
    plt.plot(x, y, col)

class Classifier:

    def Classifier(self):
        pass

    def obj(self, x):
        return 0.5 * np.dot(x.T, np.dot(self.P, x)) + np.dot(self.q, x)

    def solve(self):
#        d = [ 
#                [(0, 0), 0], #non linear separable
#                [(0, 1), 0],
#                [(1, 0), 0],
#                [(1, 1), 1],
#            ]
#        d = [ 
#                [(1, 2), -1],
#                [(1, 4), -1],
#                [(3, 4), -1],
#                [(3, 1), 1],
#                [(4, 2), 1],
#            ]
#        d = [ 
#                [(110, 130), -1],
#                [(90, 120), -1],
#                [(85, 180), -1],
#                [(120, 80), -1],
#                [(130, 180), -1],
#                [(180, 50), 1],
#                [(200, 75), 1],
#                [(165, 60), 1],
#                [(190, 65), 1],
#            ]
        d = [ 
                [(0.3858, 0.4687), 1],
                [(0.4871, 0.611), -1],
                [(0.9218, 0.4103), -1],
                [(0.7382, 0.8936), -1],
                [(0.1763, 0.0579), 1],
                [(0.4057, 0.3529), 1],
                [(0.9355, 0.8132), -1],
                [(0.2146, 0.0099), 1],
            ]
        c0 = getclass(d, -1)
        c1 = getclass(d, 1)
        P = []
        tot = len(d)
        data = c0 + c1
        for data1, class1 in data:
            r = []
            for data2, class2 in data:
                d = np.dot(data1, data2)
                c = class1 * class2
                r.append(d * c)
            P.append(r)
        G = []
        for i in range(len(data)):
            r = []
            for j in range(len(data)):
                r.append(i == j)
            G.append(r)
        A = [[-1] * len(c0) + [1] * len(c1)]
        q = [-1] * len(data)
        cons = [
                {'type':'ineq', 'fun' : lambda x : np.dot(G, x)},
                {'type':'eq', 'fun' : lambda x : np.dot(A, x)}
               ]
        self.q = q
        self.P = P
        res_cons = optimize.minimize(self.obj, [0] * len(data), constraints = cons, method = 'SLSQP')
        sol = res_cons.x
        w = np.array([0, 0])
        s = 0
        for d in c0, c1:
            l = s
            for dat, cl in d:
                w = w + cl * sol[l] * np.array(dat)
                l += 1
            s += len(d)

        b = []
        s = 0
        for d in c0, c1:
            l = s
            for dat, cl in d:
                if sol[l] >= 1e-3:
                    bx = 1 / cl - np.dot(w, dat)
                    b.append(bx)
                l += 1
            s += len(d)
        print(w, sum(b) / len(b))
        pl(c0, 'go')
        pl(c1, 'yo')
        drawline(w, sum(b) / len(b), 'r')
        drawline(w, sum(b) / len(b) - 1, 'g')
        drawline(w, sum(b) / len(b) + 1, 'g')
        plt.show()

def main():
    cls = Classifier()
    cls.solve()

main()
