#!/bin/python

from model import EssayModel
from model import load_from_file
import time

def mlda(el):
    w = set()
    for i in el:
        for j in i:
            w.add(j)

    idw = {}
    c = 0
    for i in w:
        idw[c] = i
        c += 1

    corp = []
    for i in el:
        r = []
        for j in range(c):
            if idw[j] in i:
                r.append((j, i.count(idw[j])))
        corp.append(r)

    lda_model = gensim.models.LdaModel(corp, num_topics=4, id2word=idw, passes=14)
    bgw = set()
    for i in range(lda_model.num_topics):
        t = lda_model.show_topic(i)
        for j in t:
            bgw.add(j[1])
    return list(bgw)

def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    essay = data[2][1:]
    score = data[6][1:]
    train_len = 150
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    s = time.time()
    load = False
    sk = True
    mins = min(score)
    maxs = max(score)
    if load:
        model = load_from_file('c2.model')
    else:
        model = EssayModel()
        model.train(train_essay, train_score, mins, maxs, sk)
        model.score(test_essay, test_score)
        #model.dump('c2.model')
        #print("Model dumped\n")
    print("Total time", time.time() - s)
    input('enter..')
    while True:
        s = input('Write an essay\n')
        t = model.predict([s])[0]
        print(t)
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

if __name__ == "__main__" and __package__ is None:
    __package__ = "root"
    
main()
