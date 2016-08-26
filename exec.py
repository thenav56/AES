#!/bin/python

from model import EssayModel
from model import load_from_file
from ftransform import BaseFeatureTransform
from cbfs import Cbfs
from grammar.evaluate import Evaluate
import time
import matplotlib.pyplot as plot

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
    load = False
    mins = min(score)
    maxs = max(score)
    if load:
        model = load_from_file('c2.model')
    else:
        sk = False
        if sk:
            from sklearn import svm
            mod = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
        else:
            import msvm
            mod = msvm.MSVM()
        feature = BaseFeatureTransform()
        #feature = Cbfs()
        model = EssayModel(mod, feature)
        s = time.time()
        print('training')
        model.train(train_essay, train_score, mins, maxs)
        print('total time', time.time() - s)
        input('ok..')
        model.score(test_essay, test_score)
        #model.dump('c2.model')
        #print("Model dumped\n")
    ev = Evaluate()
    ev.calc_confusion(model.target, model.predicted, 2, 12)
    ev.ROC_parameters()
    roc = ev.roc
    labels = ['Class{0}'.format(i) for i in range(2,12)]
    fig = plot.figure()
    ax = fig.add_subplot(111)
    plot.plot(roc[0], roc[1], 'ro')
    plot.plot([0,1],[0,1],'k-', lw=2)
    for label, x, y in zip(labels, roc[0], roc[1]):
        ax.annotate(
                label,
                xy = (x,y), xytext = (-20,20), textcoords='offset points')
    plot.show()
    

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
