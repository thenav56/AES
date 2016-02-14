#!/usr/bin/python
#NON-LINEAR SOFT MARGIN CLASSIFIER TEST
from math import *
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

C = 1000

class Classifier:

    def Classifier(self):
        pass

    def obj(self, x):
        return 0.5 * np.dot(x.T, np.dot(self.P, x)) + np.dot(self.q, x)

    def kernel(self, a, b):
        s = np.dot(a, b) + 1
        return s * s

    def computeWX(self, data, sol, x):
        r = 0
        for l, i in enumerate(data):
            r += sol[l] * i[1] * self.kernel(i[0], x)
        return r

    def classify(self, d, sol, b, data):
        f = self.computeWX(d, sol, data) + b
        return 1 if f >= 0 else -1
    
    def solve(self):
        d = [ 
                [(1, 1), -1], 
                [(1, 3), -1],
                [(2, 1), -1],
                [(3, 2), -1],
                [(5, 9), -1],
                [(3, 6), 1],
                [(4, 5), 1],
                [(5, 4), 1],
                [(5, 6), 1],
                [(6, 8), 1],
            ]
        d = [
                [(0, 0), -1],
                [(0, 1), 1],
                [(1, 0), 1],
                [(1, 1), -1],
            ]
        P = []
        for data1, class1 in d:
            r = []
            for data2, class2 in d:
                td = self.kernel(data1, data2)
                c = class1 * class2
                r.append(td * c)
            P.append(r)
        G = []#lambda(i) >= 0
        for i in range(len(d)):
            r = [i == j for j in range(len(d))]
            G.append(r)
        A = [cl for _, cl in d]
        q = [-1] * len(d)
        CC = [C] * len(d) #C >= lambda(i)
        cons = [
                {'type':'ineq', 'fun' : lambda x : np.dot(G, x)},
                {'type':'ineq', 'fun' : lambda x : C - np.dot(G, x)}, #C >= lambda(i)
                {'type':'eq', 'fun' : lambda x : np.dot(A, x)} #summation(y(i)*lambda(i)) = 0
               ]
        self.q = q
        self.P = P
        res_cons = optimize.minimize(self.obj, [0] * len(d), constraints = cons, method = 'SLSQP')
        sol = res_cons.x
        b = []
        s = 0
        for l, i in enumerate(d):
            if sol[l] >= 1e-5 and sol[l] < C: #if a support vector
                bx = i[1] - self.computeWX(d, sol, i[0])
                b.append(bx)
        b = sum(b) / len(b)
        for dat, cl in d:
            print(self.classify(d, sol, b, dat), 'act', cl)

def main():
    cls = Classifier()
    cls.solve()

main()
