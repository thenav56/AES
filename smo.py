#!/bin/python
import numpy as np
from random import shuffle
from random import randint

tol = 1e-3
eps = 1e-5
iters = 0#FOR TEMPORARY USE

class BSVM:

    def __init__(self, data, target, C = 1):
        self.data = data
        self.target = target
        self.b = None
        self.alpha = None
        self.N = len(self.data)
        self.C = C
        self.tot_list = [i for i in range(self.N)]
        self.error_cache = None


        self.main_routine()

    def kernel(self, a, b):
        s = np.dot(a, b) + 1
        return s * s

    def func(self, ind):
        r = 0
        for i, d in enumerate(self.data):
            if self.alpha[i] > 0:
                r += self.alpha[i] * self.target[i] * self.kernel(self.data[ind], d)
        return r - self.b

    def getError(self, ind):
        return self.error_cache[ind]
        if self.alpha[ind] > 0 and self.alpha[ind] < self.C:
            return self.error_cache[ind]
        return self.func(ind) - self.target[ind]

    def classify(self, x):
        r = 0
        for i in range(self.N):
            if self.alpha[i] > 0:
                d = self.data[i]
                r += self.alpha[i] * self.target[i] * self.kernel(d, x)
        return 1 if r - self.b >= 0 else -1

    def takestep(self, i1, i2):
        if i1 == i2:
            return 0
        #global iters
        #iters += 1
        #print(iters)
        alph1 = self.alpha[i1]
        alph2 = self.alpha[i2]
        y1 = self.target[i1]
        y2 = self.target[i2]
        bold = self.b
        s = y1 * y2
        gamma = alph1 + s * alph2
        if s == -1:
            L = max(0, alph2 - alph1)
            H = min(self.C, self.C + alph2 - alph1)
        else:
            L = max(0, alph1 + alph2 - self.C)
            H = min(self.C, alph1 + alph2)
        if L == H:
            return 0
        k11 = self.kernel(self.data[i1], self.data[i1])
        k12 = self.kernel(self.data[i1], self.data[i2])
        k22 = self.kernel(self.data[i2], self.data[i2])
        eta = 2 * k12 - k11 - k22
        E1 = self.getError(i1)
        E2 = self.getError(i2)
        if eta < 0:
            a2 = alph2 - y2 * (E1 - E2) / eta
            if a2 < L:
                a2 = L
            elif a2 > H:
                a2 = H
        else: #WHY??
            #print('here')
            v1 = self.getError(i1) + y1 + bold - y1 * alph1 * k11 - y2 * alph2 * k12
            v2 = self.getError(i2) + y2 + bold - y1 * alph1 * k12 - y2 * alph2 * k22
            objective = lambda a: \
                a * (1 - s) \
                        - 0.5 * k11 * ((gamma - s * a) ** 2) \
                        - 0.5 * k22 * a * a \
                        - (gamma - s * a) * (s * k12 * a + y1 * v1) \
                        - y2 * a * v2
            Lobj = objective(L)
            Hobj = objective(H)
            if Lobj > Hobj + eps:
                a2 = L
            elif Lobj < Hobj - eps:
                a2 = H
            else:
                a2 = alph2
            
        if abs(a2) < 1e-8:
            a2 = 0
        elif abs(a2 - self.C) < 1e-8:
            a2 = self.C
        if abs(a2 - alph2) < eps * (a2 + alph2 + eps):
            return 0
        a1 = alph1 + s * (alph2 - a2)
        if a1 < 0:
            a1 = 0
        b1 = bold + E1 + y1 * (a1 - alph1) * k11 + y2 * (a2 - alph2) * k12
        b2 = bold + E2 + y1 * (a1 - alph1) * k12 + y2 * (a2 - alph2) * k22
        b = (b1 + b2) / 2
        self.b = b
        self.alpha[i1] = a1
        self.alpha[i2] = a2
        for i in range(self.N):
#UPDATE ONLY NON-BOUND ALPHA? 
            kr1 = self.kernel(self.data[i1], self.data[i])
            kr2 = self.kernel(self.data[i2], self.data[i])
            self.error_cache[i] += y1 * (a1 - alph1) * kr1 + \
            y2 * (a2 - alph2) * kr2 + bold - self.b
        return 1

    def ex_example(self, i2):
        y2 = self.target[i2]
        alph2 = self.alpha[i2]
        E2 = self.getError(i2)
        r2 = E2 * y2
        if (r2 < -tol and alph2 < self.C) or (r2 > tol and alph2 > 0): #HOW??
            c = 0
            for i in range(self.N):
                if 0 < self.alpha[i] < self.C:
                    c += 1
            if c > 1:
                i1 = -1
                if E2 > 0:
                    for i in range(self.N):
                        if i != i2 and 0 < self.alpha[i] < self.C:
                            if i1 == -1 or self.getError(i) < err:
                                i1 = i
                                err = self.getError(i)
                else:
                    for i in range(self.N):
                        if i != i2 and 0 < self.alpha[i] < self.C:
                            if i1 == -1 or self.getError(i) > err:
                                i1 = i
                                err = self.getError(i)
                if i1 == -1:
                    print(E2)
                    assert(i1 != -1)
                if self.takestep(i1, i2):
                    return 1
            inbound = [i for i in range(self.N) if 0 < self.alpha[i] < self.C]
#RANDOMNESS leading to different training times
            #shuffle(inbound)
            for i1 in inbound:
                if self.takestep(i1, i2):
                    return 1
            #shuffle(self.tot_list)
            for i1 in self.tot_list:
                if self.takestep(i1, i2):
                    return 1
        return 0

    def main_routine(self):
        self.alpha = [0 for i in range(self.N)]
#func(i) = 0 for all i since alpha[i] = 0 and b = 0
#So initial error = func(i) - self.target[i] = -self.target[i]
        self.error_cache = [-self.target[i] for i in range(self.N)]
        self.b = 0
        numChanged = 0
        examineAll = 1
        while numChanged > 0 or examineAll:
            numChanged = 0
            if examineAll:
                for i in range(self.N):
                    numChanged += self.ex_example(i)
            else:
                for i in range(self.N):
                    if 0 < self.alpha[i] < self.C:
                        numChanged += self.ex_example(i)
            if examineAll == 1:
                examineAll = 0
            elif numChanged == 0:
                examineAll = 1
            #print(self.alpha)
        
        #print('Converged')
        print(self.alpha)
        #print(self.b)

    def evaluate_on_train_data(self):
        r = 0
        for i in range(self.N):
            c = 1 if self.classify(self.data[i]) >= 0 else -1
            print(c, self.target[i])
            r += c == self.target[i]
        print('Accuracy', r / self.N)

def main():
    data = [
        [0.3858, 0.4687],
        [0.4871, 0.6110],
        [0.9218, 0.4103],
        [0.7382, 0.8936],
        [0.1763, 0.0579],
        [0.4057, 0.3529],
        [0.9355, 0.8132],
        [0.2146, 0.0099],
    ]
    target = [1, -1, -1, -1, 1, 1, -1, 1]
    r = BSVM(data, target, 10)
    r.evaluate_on_train_data()

if __name__ == "__main__":
    main()
