#!/usr/bin/python
#binary svm
from math import *
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

class BSVM:

    def __init__(self, dataset, C = 1000):
        self.dataset = dataset
        self.lambdas = None
        self.b = None
        self.C = C
        self.support_vectors = None
        self.build()

    def obj(self, x):
        return 0.5 * np.dot(x.T, np.dot(self.P, x)) + np.dot(self.q, x)

    def kernel(self, a, b):
        s = np.dot(a, b) + 1
        return s * s

    def computeSupportVectors(self):
        self.support_vectors = [i for i in range(len(self.dataset)) if self.lambdas[i] >= 1e-5]

    def computeWX(self, x):
        r = 0
        for i in self.support_vectors:
            d = self.dataset[i]
            r += self.lambdas[i] * d[1] * self.kernel(d[0], x)
        return r

    def classify(self, data):
        f = self.computeWX(data) + self.b
        return 1 if f >= 0 else -1
    
    def build(self):
        P = []
        for data1, class1 in self.dataset:
            r = []
            for data2, class2 in self.dataset:
                td = self.kernel(data1, data2)
                c = class1 * class2
                r.append(td * c)
            P.append(r)
        G = []#lambda(i) >= 0
        for i in range(len(self.dataset)):
            r = [i == j for j in range(len(self.dataset))]
            G.append(r)
        A = [cl for _, cl in self.dataset]
        q = [-1] * len(self.dataset)
        cons = [
                {'type':'ineq', 'fun' : lambda x : np.dot(G, x)},
                {'type':'ineq', 'fun' : lambda x : self.C - np.dot(G, x)}, #C >= lambda(i)
                {'type':'eq', 'fun' : lambda x : np.dot(A, x)} #summation(y(i)*lambda(i)) = 0
               ]
        self.q = q
        self.P = P
        res_cons = optimize.minimize(self.obj, [0] * len(self.dataset), constraints = cons, method = 'SLSQP')
        self.lambdas = res_cons.x
        self.computeSupportVectors()
        b = []
        s = 0
        for l, i in enumerate(self.dataset):
            if self.lambdas[l] >= 1e-5 and self.lambdas[l] < self.C: #if a support vector
                bx = i[1] - self.computeWX(i[0])
                b.append(bx)
        self.b = sum(b) / len(b)

    def evaluate(self):
        for dat, cl in self.dataset:
            print(self.classify(dat), 'act', cl)

def main():
    d = [
            [(0, 0), -1],
            [(0, 1), 1],
            [(1, 0), 1],
            [(1, 1), -1],
        ]
    cls = BSVM(d)
    cls.build()
    cls.evaluate()

if __name__ == "__main__":
    main()
