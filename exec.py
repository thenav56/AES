#!/bin/python

from msvm import MSVM
from sklearn import svm
from random import shuffle
import time
import string
import numpy as np

import csv

def isfloat(n):
    try:
        float(n)
        return 1
    except ValueError:
        return 0

def withsk(data, test, rows, out_features, out_class, pr = False):
    train_set = []
    train_target = []
    for a, b in data:
        train_set.append(a)
        train_target.append(b)
    cl = svm.SVC(kernel = 'poly', degree = 2)
    cl.fit(train_set, train_target)
    o = cl.predict(test)
    o = list(o)
    print('sk', cl.score(train_set, train_target)) 
    if pr:
        print(','.join(out_features + [out_class]))
        for i, c in enumerate(o):
            s = ",".join(str(j) for j in rows[i])
            print(s + ',' + str(c))
    r = cl.support_
#    for i, j in enumerate(r):
#        print(data[j], cl.support_vectors_[i])
#        print(data[j])
#        input()

def transform(data, features, header, dic):
    r = []
    for j in features:
        ind = header.index(j)
        if j in dic:
            for k in dic[j]:
                r.append(1 if data[ind] == k else 0)
        else:
            r.append(float(data[ind]))
    return np.array(r)

def process(d):
    r = []
    for i in d:
        i = i.lower()
        if '@' not in i[0]:
            t = [j for j in i if j in string.ascii_lowercase]
            r.append(''.join(t))
    return r

def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    essay = data[2][1:]
    essay = [i.split() for i in essay]
    essay = [process(i) for i in essay]
    score = data[6][1:]
    bagofwords = set()
    for i in essay:
        for j in i:
            bagofwords.add(j)
    print(len(bagofwords))
    for i in bagofwords:
        print(i)

main()
