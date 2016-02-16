#!/usr/bin/python
#multiclass SVM
from math import *
import numpy as np
from bsvm import BSVM
from scipy import optimize
import matplotlib.pyplot as plt

class MSVM:

    def __init__(self, dataset, C = 10):
        self.dataset = dataset
        self.C = C
        self.support_vectors = None
        self.classes = None
        self.bsvms = None # 3-tuple (class corresponding to +ve class, cls corr -ve, binarysvm)
        self.build()

    def classify(self, data):
        if len(self.classes) == 1:
            return self.classes[0]
        votes = {}
        for i in self.classes:
            votes[i] = [0, 0]
        for cl1, cl2, svm in self.bsvms:
            r = svm.classify(data)
            if r > 0:
                votes[cl1][0] += 1
                votes[cl1][1] += r
            else:
                votes[cl2][0] += 1
                votes[cl2][1] -= r
        #mv = max(self.classes, key = lambda cl: votes[cl]) #xXx
        #for i in votes:
        #    if votes[mv] == votes[i]:
        #        print('A')
        return max(self.classes, key = lambda cl: votes[cl]) #xXx

    def build(self):
        classes = set(i for _, i in self.dataset)
        classes = [i for i in classes]#convert above to array
        self.classes = classes
        dict_cls = {}
        for i in classes:
            dict_cls[i] = []
        for a, b in self.dataset:
            dict_cls[b].append(a)
        if len(classes) > 1:
            self.bsvms = []
            for i in range(len(classes)):
                for j in range(i + 1, len(classes)):
                    cl1 = classes[i]#+ve class
                    cl2 = classes[j]#-ve class
                    d1 = [(a, 1) for a in dict_cls[cl1]]
                    d2 = [(a, -1) for a in dict_cls[cl2]]
                    self.bsvms.append([cl1, cl2, BSVM(d1 + d2, self.C)])

def main():
    pass

if __name__ == "__main__":
    main()
