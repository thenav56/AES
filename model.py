import pickle
import string
import math
import numpy as np

class EssayModel:

    def __init__(self, model, feature_transform):
        self.datasets = None
        self.target = None

        self.model = model
        self.ftransform = feature_transform
        self.predicted = []

    def score(self, datasets, targets):
        self.target = targets
        acc = 0
        sum_a = 0
        sum_p = 0
        sum_aa = sum_pp = 0
        sum_ap = 0
        print('min max scor', self.min_score, self.max_score)
        tot_dist = 0
        L = self.min_score
        U = self.max_score
        predict = {i : 0 for i in range(L, U + 1)}
        actual = {i : 0 for i in range(L, U + 1)}
        #running kappa calculator
        for i, j in enumerate(datasets):
            v = self.ftransform.getTransformed([j])[0]
            p = self.model.predict([v])[0]
            self.predicted.append(p)
            predict[p] += 1
            actual[targets[i]] += 1
            acc += p == targets[i]
            sum_a += targets[i]
            sum_p += p
            sum_ap += p * targets[i]
            sum_aa += targets[i] * targets[i]
            sum_pp += p * p
            jac = acc / (i + 1.0)
            dist = lambda a, b: (a - b) ** 2 / float((self.max_score - self.min_score) ** 2)
            tot_dist += dist(p, targets[i])
            disagree = 0
            #compute the probability of random disagreement
            N = float(i + 1)
            for k in range(L, U + 1):
                for l in range(L, U + 1):
                    if k != l:
                        p1 = predict[k] / N
                        p2 = actual[l] / N
                        disagree += p1 * p2 * dist(k, l)
            dist_normalized = tot_dist / (i + 1.0)
            print('rand agreement', 1 - disagree)
            #if raters are more likely to accept in random, penalize the observed distance
            kappa = 1 - min(1, 1 if disagree == 0 else dist_normalized / disagree)
            print('test set fit %', jac * 100, 'actual', targets[i], 'predicted', p, 'kappa %', kappa * 100);

        n = len(datasets)
        den = math.sqrt(n * sum_aa - sum_a * sum_a) * math.sqrt(n * sum_pp - sum_p * sum_p);
        if den:
            cor = (n * sum_ap - sum_a * sum_p) / den
            print('correlation', cor)

    def train(self, datasets, scores, min_score, max_score):
        self.ftransform.setDataSet(datasets, scores)
        datasets = self.ftransform.getTransformed(datasets, False)
        self.min_score = min_score
        self.max_score = max_score
        print('training start')
        self.model.fit(datasets, scores)
        #print('fitness', self.model.score(datasets, scores))
        print('training finished')
    
    def predict(self, datasets): 
        v = self.ftransform.getTransformed(datasets)
        return self.model.predict(v)

    def dump(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

def load_from_file(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

