#!/bin/python

from msvm import MSVM
from sklearn import svm
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
    print(cl.score(train_set, train_target)) 
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

def main():
    with open('train.csv', 'r') as f:
        data = csv.reader(f, delimiter=',')
        data = [i for i in data]
        header = data[0]
        data = data[1:]

    features = ['Sex', 'Pclass', 'SibSp']
    out_class = 'Survived'
    class_id = header.index(out_class)
    data_set = []
    dic = {}
    for i in data:
        for j in features:
            ind = header.index(j)
            if not isfloat(i[ind]):
                if j not in dic:
                    dic[j] = set()
                dic[j].add(i[ind])
    for k in dic:
        dic[k] = list(dic[k])
    train_set = []
    for i in data:
        r = transform(i, features, header, dic)
        train_set.append([r, i[class_id]])
    test_set = []
    out_features = ['PassengerId']
    rows = []
    with open('test.csv', 'r') as f:
        data = csv.reader(f, delimiter=',')
        data = [i for i in data]
        header = data[0]
        data = data[1:]
        for i in data:
            r = transform(i, features, header, dic)
            d = []
            for j in out_features:
                d.append(i[header.index(j)])
            rows.append(d)
            test_set.append(r)
    withsk(train_set, test_set, rows, out_features, out_class)
    model = MSVM(train_set, 1)
    v = 0
    for d, c in train_set:
        r = model.classify(d)
        #print(c, r)
        v += int(c == r)
    print('Accuracy', v / len(train_set))

main()
