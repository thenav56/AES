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
        n = len(x)
        r = 0
        #for i in range(n):
        #    for j in range(n):
        #        r += x[i] * x[j] * self.P[i][j]
        #return 0.5 * r - sum(x)
        return 0.5 * np.dot(x.T, np.dot(self.P, x)) + np.dot(self.q, x)

    def kernel(self, a, b):
        s = np.dot(a, b) + 1
        return s * s

    def computeSupportVectors(self):
        self.support_vectors = [i for i in range(len(self.dataset)) if self.lambdas[i] >= 1e-5 and self.lambdas[i] < self.C]

    def computeWX(self, x):
        r = 0
        for i in self.support_vectors:
            d = self.dataset[i]
            r += self.lambdas[i] * d[1] * self.kernel(d[0], x)
        return r

    def classify(self, data):
        f = self.computeWX(data) + self.b
        return f
    
    def build(self):
        P = []
        for data1, class1 in self.dataset:
            r = []
            for data2, class2 in self.dataset:
                td = self.kernel(data1, data2)
                c = class1 * class2
                r.append(td * c)
            P.append(np.array(r))
        A = np.array([cl for _, cl in self.dataset])
        q = np.array([-1] * len(self.dataset))
        self.q = q
        self.P = P
        cons = [
                {'type':'ineq', 'fun' : lambda x : x}, # lambda(i) >= 0
                {'type':'ineq', 'fun' : lambda x : self.C - x}, #C >= lambda(i)
                {'type':'eq', 'fun' : lambda x : np.dot(A, x)} #summation(y(i)*lambda(i)) = 0
               ]
        print('minimizing')
        res_cons = optimize.minimize(self.obj, np.array([0] * len(self.dataset)), constraints = cons, method = 'SLSQP')
        print('done')
        self.lambdas = res_cons.x
        print(self.lambdas)
        self.computeSupportVectors()
        b = []
        s = 0
        for l, i in enumerate(self.support_vectors):
            bx = self.dataset[l][1] - self.computeWX(self.dataset[i][0])
            b.append(bx)
        self.b = sum(b) / len(b)

def main():
    pass

if __name__ == "__main__":
    main()

