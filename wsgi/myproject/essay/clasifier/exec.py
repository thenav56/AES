#!/bin/python

from model import EssayModel
from model import load_from_file
import time


def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    essay = data[2][1:]
    score = data[6][1:]
    train_len = 200  # training set size
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    train_essay = [i.split() for i in train_essay]
    test_essay = [i.split() for i in test_essay]
    s = time.time()
    load = False
    if load:
        model = load_from_file('c2.model')
    else:
        model = EssayModel()
        model.train(train_essay, train_score)
        model.dump('c2.model')
        print("Model dumped\n")
    print("Total time", time.time() - s)
    print(len(model.target))
    while True:
        s = input('Write an essay\n').split()
        t = model.predict([s])[0]
        print(t)
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

main()
