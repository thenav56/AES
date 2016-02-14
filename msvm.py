#!/usr/bin/python
#multiclass SVM
from math import *
import numpy as np
from bsvm import BSVM
from scipy import optimize
import matplotlib.pyplot as plt

class MSVM:

    def __init__(self, dataset, C = 1000):
        self.dataset = dataset
        self.C = C
        self.support_vectors = None
        self.oneclass = False
        self.decision = None
        self.classes = None
        self.bsvms = None # 3-tuple (class corresponding to +ve class, cls corr -ve, binarysvm)
        self.build()

    def classify(self, data):
        if self.oneclass:
            return self.decision
        votes = {}
        for i in self.classes:
            votes[i] = 0
        for cl1, cl2, svm in self.bsvms:
            r = svm.classify(data)
            if r == 1:
                votes[cl1] += 1
            else:
                votes[cl2] += 1
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
        if len(classes) == 1:
            self.oneclass = True
            self.decision = classes[0]
        else:
            self.bsvms = []
            for i in range(len(classes)):
                for j in range(i + 1, len(classes)):
                    cl1 = classes[i]#+ve class
                    cl2 = classes[j]#-ve class
                    d1 = [(a, 1) for a in dict_cls[cl1]]
                    d2 = [(a, -1) for a in dict_cls[cl2]]
                    self.bsvms.append([cl1, cl2, BSVM(d1 + d2, self.C)])

    def evaluate(self):
        for dat, cl in self.dataset:
            print(dat, 'classified as', self.classify(dat), 'actual class', cl)

def main():
    d = [
            [(0, 0), 0],
            [(0, 1), 1],
            [(1, 0), 1],
            [(1, 1), 0],
        ]
    cls = MSVM(d)
    cls.evaluate()

if __name__ == "__main__":
    main()
