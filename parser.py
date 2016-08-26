#!/usr/bin/python3

def loadfiles():
    with open('files', 'r') as f:
        r = []
        for i in f:
            if i:
                if i[-1:] == '\n':
                    i = i[:-1]
                if i[-1:] != '~':
                    r += i,
        return r
    return []

from model import EssayModel
from model import load_from_file
from ftransform import BaseFeatureTransform
from cbfs import Cbfs
from grammar.evaluate import Evaluate
import time
import matplotlib.pyplot as plot

def empty(s):
    import string
    for i in s:
        if i.lower() in string.ascii_lowercase:
            return False
    return True

def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    essay = data[2][1:]
    score = data[6][1:]
    train_len = 1200
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    test_essay = essay[train_len:]
    test_score = score[train_len:]
    s = time.time()
    mins = min(score)
    maxs = max(score)
    names = loadfiles()
    essay_list = []
    for i in names:
        with open('g8/' + i, 'r') as f:
            name = None
            title = None
            core = ""
            for i in f:
                if not empty(i):
                    if name == None:
                        name = i
                    elif title == None:
                        title = i
                    else:
                        core += i
            essay_list.append([name, core])
    for i in essay_list:
        print(i)
    model = load_from_file('twelve.model')
    for i in essay_list:
        print(i[0], 'scores', model.predict([i[1]]))
        input('...')
    #model.score(test_essay, test_score)
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
