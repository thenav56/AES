import numpy as np

class Evaluate:
    def __init__(self):
        self.confusion = None
        self.scores = None
        self.startscore = None
        self.endscore = None
        self.roc = None
    
    def calc_confusion(self, score1, score2, mins, maxs):
        self.startscore = mins
        self.endscore = maxs
        n = self.endscore - self.startscore + 1
        mat = np.zeros((n,n), dtype=int)
        for i in range(len(score1)):
            mat[score1[i]-self.startscore,score2[i]-self.startscore] += 1
        self.confusion = mat

    def truep(self, index):
        return self.confusion[index-self.startscore][index-self.startscore]

    def truen(self, index):
        mat = np.array(self.confusion)
        mat = np.delete(mat,index-self.startscore,0)
        mat = np.delete(mat,index-self.startscore,1)
        return mat.sum()

    def falsep(self, index):
        mat = self.confusion.sum(axis=0)
        return mat[index-self.startscore] - self.confusion[index-self.startscore][index-self.startscore]

    def falsen(self, index):
        mat = self.confusion.sum(axis=1)
        return mat[index-self.startscore] - self.confusion[index-self.startscore][index-self.startscore]

    def accuracy(self,index):
        tp = self.truep(index)
        tn = self.truen(index)
        fp = self.falsep(index)
        fn = self.falsen(index)
        if(tp+tn+fp+fn != 0):
            return (tp+tn)/(tp+tn+fp+fn)
        else:
            return 0

    def precision(self, index):
        tp = self.truep(index)
        fp = self.falsep(index)
        if(tp+fp != 0):
            return tp/(tp+fp)
        else:
            return 0

    def TPR(self, index):
        tp = self.truep(index)
        fn = self.falsen(index)
        if(tp+fn != 0):
            return tp/(tp+fn)
        else:
            return 0

    def FPR(self,index):
        fp = self.falsep(index)
        tn = self.truen(index)
        if(fp+tn != 0):
            return fp/(fp+tn)
        else:
            return 0

    def ROC_parameters(self):
        tpr = []
        fpr = []
        for i in range(self.startscore, self.endscore):
            tpr.append(self.TPR(i))
            fpr.append(self.FPR(i))
        data = list(zip(fpr,tpr))
        self.roc = data
            
        
def main():
    scores = [2,4,3,5,5,6,7,8,9,10,11,12]
    ev = Evaluate()
    x = [3,5,6,2,12]
    y = [3,3,4,3,11]
    ev.calc_confusion(x,y, 2, 12)
    acc = ev.accuracy(3)
    print(acc)
    print(ev.precision(5))
    ev.ROC_parameters()
    print(ev.roc)


