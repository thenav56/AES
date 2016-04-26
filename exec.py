#!/bin/python

from msvm import MSVM
from sklearn import svm
from random import shuffle
import time
import string
import numpy as np
import math

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

def loadspellcorrector():
    dictfile = "cspell/files/big.txt"
    import importlib.util
    spec = importlib.util.spec_from_file_location("cspell", "cspell/spell_corrector/cspell.py")
    cs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cs)
    return cs.cspell(dictfile)

def euc_dissimilarity(a, b):
    return sum((i - j) ** 2 for i, j in zip(a, b))

def cos_dissimilarity(a, b):
    m1 = math.sqrt(sum(i * i for i in a))
    m2 = math.sqrt(sum(i * i for i in b))
    return -sum(i * j for i, j in zip(a, b)) / (m1 * m2)

def vectorize(essay, bagofwords):
    return [essay.get(i, 0) for i in bagofwords]

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
    cp = loadspellcorrector()#spell corrector
    #correct minor spell errors using spell corrector
    essay = [[cp.best_word(j) for j in i] for i in essay]
    ns = []
    for i in essay:
        dct = {}
        for j in i:
            dct[j] = dct.get(j, 0) + 1
        ns.append(dct)
    essay = ns
#total essays 1783
    train_len = 1700 #training set size
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    bagofwords = set()

    for i in train_essay:
        for j in i:
            if j != None: #None is a major spell error
                bagofwords.add(j)
    
    bagofwords = list(bagofwords) #dimension
    train_vectors = [vectorize(i, bagofwords) for i in train_essay]
    test_vectors = [vectorize(i, bagofwords) for i in test_essay]
    
    for test, score in zip(test_vectors, test_score):
        mindist = 1e15
        bstcls = -1
        print('classify')
        for d, s in zip(train_vectors, train_score):
            dist = euc_dissimilarity(d, test)
            if dist < mindist:
                bstcls = s
                mindist = dist
        print(score, ' classified as ', bstcls)


main()
