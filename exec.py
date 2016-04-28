#!/bin/python

import msvm
from sklearn import svm
from random import shuffle
import pickle
import time
import string
import numpy as np
import math
import csv

def loadspellcorrector():
    dictfile = "cspell/files/big.txt"
    import importlib.util
    spec = importlib.util.spec_from_file_location("cspell", "cspell/spell_corrector/cspell.py")
    cs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cs)
    return cs.cspell(dictfile)

class EssayModel:

    def __init__(self):
        self.bagofwords = None
        self.idf_vector = None
        self.model = None
        self.essays = None
        self.train_vectors = None
        self.target = None

    #essay is an essay(??)
    #returns an essay
    def preprocess(self, essay):
        r = []
        for i in essay:
            i = i.lower()
            if '@' not in i:
                t = ''.join(j for j in i if j in string.ascii_lowercase)
                r.append(t)
        return r

    #essay is list of essay
    def preprocess_set(self, essay):
        cp = loadspellcorrector()#spell corrector
        #correct minor spell errors using spell corrector
        allwords = set(j for i in essay for j in i)
        bword = {}
        for i in allwords:
            bword[i] = cp.best_word(i)
        essay = [[bword[j] for j in i] for i in essay]
        return essay

    #convert essay string into a dictionary
    def essaytodict(self, essay):
        dct = {}
        for j in essay:
            dct[j] = dct.get(j, 0) + 1
        return dct

    #"essays" is a list of essay
    #"scores" consists of the corresponding score of an essay in "essays"
    def train(self, essays, scores):
        #first remove named entities, punctuations, etc...
        essays = [self.preprocess(i) for i in essays]

        #now remove spell errors from whole set
        essays = self.preprocess_set(essays)
        essays = [self.essaytodict(i) for i in essays]
        #now obtain parameters(bags,idf) from the train set
        self.parameters_from_essays(essays)

        #now vectorize each essay string
        self.train_vectors = [self.vectorize(i) for i in essays]
        #now train the vectors using a classifier
        whole = list(zip(self.train_vectors, scores))
        print("training own")
        self.model = msvm.MSVM(whole)
        self.target = scores
        print("finished own")
        print('fitness:', self.model.score(self.train_vectors, scores))
    
    #vectorize an essay (list of words)
    def vectorize_raw(self, essay):
        return self.vectorize(self.essaytodict(self.preprocess(essay)))

    def score(self, essays, targets):
        t = 0
        for i, j in enumerate(essays):
            r = self.vectorize_raw(j)
            res = self.model.classify(r)
            t += targets[i] == res
            print('score ', targets[i], 'prediction', res, 'acc', t / (i + 1))

    #predict score of essays, essay is a list of words
    def predict(self, essays): 
        return [self.model.classify(self.vectorize_raw(i)) for i in essays]

    def parameters_from_essays(self, essays):
        bagofwords = set()
        docfreq = {}
        for i in essays:
            for j in i:
                if j != None: #None is a major spell error
                    bagofwords.add(j)
                    docfreq[j] = docfreq.get(j, 0) + 1
        bagofwords = list(bagofwords) #dimension
        idf_v = []#idf vector
        for i in bagofwords:
            idf = math.log(len(essays) / (1 + docfreq[i]))
            idf_v.append(idf)

        self.idf_vector = idf_v
        self.bagofwords = bagofwords

    #essay is a dict word:count
    def vectorize(self, essay):
        v = []
        for r, i in enumerate(self.bagofwords):
            tf = essay.get(i, 0)
            v.append(tf * self.idf_vector[r])
        #v.append(essay.get(None, 0))#incorrect spellings
        #v.append(sum(i for _, i in essay.items())) #length of essay in words
        return v

    def dump(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

def load_from_file(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    essay = data[2][1:]
    score = data[6][1:]
#total essays 1783
    train_len = 100 #training set size
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    train_essay = [i.split() for i in train_essay]
    test_essay = [i.split() for i in test_essay]
    #model = load_from_file('c.model')
    load = True
    if load:
        model = load_from_file('c.model')
    else:
        model = EssayModel()
        model.train(train_essay, train_score)
        model.dump('c.model')
        print("Model dumped\n")
    clf = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
    clf.fit(model.train_vectors, model.target)
    test_vectors = [model.vectorize_raw(i) for i in test_essay]
    print('sk train', clf.score(model.train_vectors, model.target))
    print('sk test', clf.score(test_vectors, test_score))
    model.score(test_essay, test_score)
#    p = clf.predict(test_vectors)
#    dc = {}
#    count = {}
#    for i, prd in enumerate(p):
#        sc = test_score[i]
#        count[sc] = count.get(sc, 0) + 1
#        if sc not in dc:
#            dc[sc] = {}
#        dc[sc][prd] = dc[sc].get(prd, 0) + 1
#
#    for k, v in dc.items():
#        for a, b in v.items():
#            print(b, "/", count[k], "CLASS", k, "classed as", a)
#
#    while True:
#        s = input('Write an essay\n')
#        s = process(s.split())
#        s = essaytodict(s)
#        s = vectorize(s, bagofwords, idf_v)
#        print(sum(s))
#        print(clf.predict([s]))

main()
