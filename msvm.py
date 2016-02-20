#!/usr/bin/python
#multiclass SVM
from math import *
import numpy as np
from bsvm import BSVM
from scipy import optimize
import matplotlib.pyplot as plt
from random import shuffle

# HOW TO USE?
# model = MSVM(dataset)
# where dataset is an array of pair of the form
# (features_list, class) where each of the element of a features_list must be
# integer or float
# class can be any alphanumeric object
# The model returned can be used to classify new
# feature set
# Just call model.classify(features_list)
# where features_list is an array of features

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
        p = 0
        for a, b in self.dataset:
            dict_cls[b].append(p)
            p += 1
        if len(classes) > 1:
            self.bsvms = []
            for i in range(len(classes)):
                for j in range(i + 1, len(classes)):
                    cl1 = classes[i]#+ve class
                    cl2 = classes[j]#-ve class
                    d1 = dict_cls[cl1]
                    d2 = dict_cls[cl2]
                    r = d1 + d2;
                    d = [self.dataset[i][0] for i in r]
                    t = [1 if self.dataset[i][1] == cl1 else -1 for i in r]
                    self.bsvms.append([cl1, cl2, BSVM(d, t)])

    def evaluate_on_train_data(self):
        r = 0
        for d, c in self.dataset:
            cr = self.classify(d)
            r += c == cr
        print('Accuracy', r / len(self.dataset))


def main():
    pass

if __name__ == "__main__":
    main()
