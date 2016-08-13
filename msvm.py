#!/usr/bin/python
#multiclass SVM
from bsvm import BSVM
import numpy as np
import pickle

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

    def predict(self, data):
        ret = []
        for vec in data:
            if len(self.classes) == 1:
                return self.classes[0]
            votes = {}
            for i in self.classes:
                votes[i] = [0, 0]
            for cl1, cl2, svm in self.bsvms:
                r = svm.classify(vec)
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
            ret.append(max(self.classes, key = lambda cl: votes[cl])) #xXx
        return ret

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
                    model = BSVM()
                    model.train(d, t)
                    self.bsvms.append([cl1, cl2, model])

    def score(self, data, target, pr = False):
        r = 0
        for i, d in enumerate(data):
            cr = self.classify(d)
            r += target[i] == cr
            if pr:
                print('running', r / (i + 1))
        return r / len(data)

def main():
    pass

if __name__ == "__main__":
    main()
