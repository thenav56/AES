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

def vectorize(essay, bagofwords, idf_vector):
    v = []
    for r, i in enumerate(bagofwords):
        tf = essay.get(i, 0)
        v.append(tf * idf_vector[r])
    #v.append(essay.get(None, 0))#incorrect spellings
    #v.append(sum(i for _, i in essay.items())) #length of essay in words
    return v

def essaytodict(essay):
    dct = {}
    for j in essay:
        dct[j] = dct.get(j, 0) + 1
    return dct

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
    allwords = set(j for i in essay for j in i)
    bword = {}
    for i in allwords:
        bword[i] = cp.best_word(i)
    essay = [[bword[j] for j in i] for i in essay]
    essay = [essaytodict(i) for i in essay]
#total essays 1783
    train_len = 1700 #training set size
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    bagofwords = set()
    docfreq = {}
    for i in train_essay:
        for j in i:
            if j != None: #None is a major spell error
                bagofwords.add(j)
                docfreq[j] = docfreq.get(j, 0) + 1
    bagofwords = list(bagofwords) #dimension
    idf_v = []#idf vector
    stopwords = []
    newbag = []
    for i in bagofwords:
        idf = math.log(train_len / (1 + docfreq[i]))
        idf_v.append(idf)
        if idf < 1:
            stopwords.append(i)
        else:
            newbag.append(i)
    #bagofwords = newbag #eliminate stop words calculated earlier ?

    print('dimensions', len(bagofwords))
    train_vectors = [vectorize(i, bagofwords, idf_v) for i in train_essay]
    test_vectors = [vectorize(i, bagofwords, idf_v) for i in test_essay]
    clf = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
    print('training svm')
    clf.fit(train_vectors, train_score)
    print('finished svm')
    #FOR TESTING OUR OWN SVM
    #model2 = MSVM(list(zip(train_vectors, train_score)))
    #print('finishedmsvm')
    #model2.evaluate_on_train_data()
    print('training set fit', clf.score(train_vectors, train_score))
    print('test set fit', clf.score(test_vectors, test_score))
    p = clf.predict(test_vectors)
    dc = {}
    count = {}
    for i, prd in enumerate(p):
        sc = test_score[i]
        count[sc] = count.get(sc, 0) + 1
        if sc not in dc:
            dc[sc] = {}
        dc[sc][prd] = dc[sc].get(prd, 0) + 1

    for k, v in dc.items():
        for a, b in v.items():
            print(b, "/", count[k], "CLASS", k, "classed as", a)
    
    while True:
        s = input('Write an essay\n')
        s = process(s.split())
        s = [cp.best_word(i) for i in s]
        s = essaytodict(s)
        s = vectorize(s, bagofwords, idf_v)
        print(clf.predict([s]))

main()
