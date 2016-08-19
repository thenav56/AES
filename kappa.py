#!/usr/bin/python3
import math
scores = [ [8, 7], [10, 9], [8, 9], [6, 6], [7, 8], [6, 7], [8, 8], [6, 8], [7, 7], [7, 6], [6, 6], [7, 7], [7, 8], [9, 9], [8, 7]]

def score():
    L = 2
    U = 12
    predict = {i : 0 for i in range(L, U + 1)}
    actual = {i : 0 for i in range(L, U + 1)}
    print('Total data sets', len(scores))
    #running kappa calculator
    predicted = list(zip(*scores))[0]
    targets = list(zip(*scores))[1]
    sum_a = sum_p = sum_ap = sum_pp = sum_aa = 0
    tot_dist = 0
    acc = 0
    for i, j in enumerate(scores):
        p = predicted[i]
        predict[p] += 1
        actual[targets[i]] += 1
        acc += p == targets[i]
        sum_a += targets[i]
        sum_p += p
        sum_ap += p * targets[i]
        sum_aa += targets[i] * targets[i]
        sum_pp += p * p
        jac = acc / (i + 1.0)
        dist = lambda a, b: (a - b) ** 2 / float((U - L) ** 2)
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

    n = len(scores)
    den = math.sqrt(n * sum_aa - sum_a * sum_a) * math.sqrt(n * sum_pp - sum_p * sum_p);
    if den:
        cor = (n * sum_ap - sum_a * sum_p) / den
        print('correlation', cor)


score()
