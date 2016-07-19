#!/bin/python

from msvm import MSVM
from sklearn import svm
from random import shuffle
import time
import string
import numpy as np
import math

import csv

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
    #L = sum(i for i in essay.values())
    for r, i in enumerate(bagofwords):
        tf = essay.get(i, 0)
        #v.append(tf)
        v.append(tf * idf_vector[r])
    err = essay.get(None, 0)
    for i in essay:
        if i not in bagofwords:
            err += essay[i]
    v.append(err)#incorrect spellings
    v.append(sum(i for _, i in essay.items())) #length of essay in words
    return v

def essaytodict(essay):
    dct = {}
    for j in essay:
        dct[j] = dct.get(j, 0) + 1
    return dct

def stopw(filename):
    swtext = open(filename, "r", encoding="latin-1")
    r = []
    for line in swtext:
        if line[-1] == '\n':
            line = line[:-1]
        r += line, 
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
    cp = loadspellcorrector()#spell corrector
    #correct minor spell errors using spell corrector
    allwords = set(j for i in essay for j in i)
    #stw = set(stopw('stop.txt'))
    bword = {}
    bagofwords = set()
    for i in allwords: 
        bword[i] = cp.best_word(i)
        if bword[i] != None:
            bagofwords.add(bword[i])
    bagofwords = list(bagofwords) #dimension
    #essay = [[bword[j] for j in i] for i in essay]
    essay = [essaytodict(i) for i in essay]
#total essays 1783
    import params
    train_len = params.get() #training set size
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    docfreq = {}
    for i in train_essay:
        for j in i:
            if j != None: #None is a major spell error
                docfreq[j] = docfreq.get(j, 0) + 1
    print(len(allwords))
    idf_v = []#idf vector
    stopwords = []
    newbag = []
    for i in bagofwords:
        idf = math.log(train_len / (1 + docfreq.get(i, 0)))
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
    print('training set fit', clf.score(train_vectors, train_score))
    print('test set fit', clf.score(test_vectors, test_score))
    print('finished svm')
    while True:
        s = input('Write an essay\n')
        s = process(s.split())
        s = essaytodict(s)
        s = vectorize(s, bagofwords, idf_v)
        print(sum(s))
        print(clf.predict([s]))

main()
