import math
import numpy as np


class Cbfs:
    def __init__(self, bag, vector, score):
        self.bagofwords = bag
        self.idf_vector = vector
        #may need to calculate the transpose
        self.score = score
        self.rff = None
        self.rcf = None
        self.autofn()

    #initiate a matrix of zeros
    def autofn(self):
        n = len(self.bagofwords)
        self.rff = np.zeros((n,n), dtype=float)

    def compute_correlation(self, x, y):
        n = len(x)
        sumx = 0 
        sumy = 0
        sumxy = 0
        sumx2 = 0
        sumy2 = 0
        for i in range(n):
            sumx += x[i]
            sumy += y[i]
            sumxy += x[i]*y[i]
            sumx2 += x[i]**2
            sumy2 += y[i]**2
        sxx= n*sumx2 - sumx**2
        syy = n*sumy2 - sumy**2
        sxy = n*sumxy - sumx*sumy

        r = sxy/math.sqrt(sxx*syy)
        return r

    #feature-feature correlation
    def compute_rff(self):
        for i in range(len(self.bagofwords)):
            for j in range(i+1, len(self.bagofwords)):
                self.rff[i][j] = self.compute_correlation(self.idf_vector[i],
                        self.idf_vector[j])

    #class-feature correlation
    def compute_rcf(self):
        r = []
        for i in range(len(self.bagofwords)):
                r.append(self.compute_correlation(self.score,
                    self.idf_vector[i]))
        self.rcf = r

    #merit in removal of index
    def merit(self, index):
        n = len(self.bagofwords) -1
        mrcf = (sum(self.rcf) - self.rcf[index])/n
        sumn = n*(n-1)/2
        trff = self.rff
        trff = np.delete(trff, index,0)
        trff = np.delete(trff, index,1)
        mrff = trff.sum()/sumn

        m = n*mrcf/math.sqrt(n+n*(n-1)*mrff)
        return m

    def ft_reduce(self, num):
        for i in range(num):
            cmerit = 0
            cindex = 0
            #find the index of feature whose removal gives highest merit
            for j in range(len(self.bagofwords)):
                merit = self.merit(j)
                if(merit > cmerit):
                    cmerit = merit
                    cindex = j
            #delete row and column for cindex
            self.rff = np.delete(self.rff, cindex, 0)
            self.rff = np.delete(self.rff, cindex, 1)
            del self.rcf[cindex]
            #removal of feature
            del self.bagofwords[cindex]
            self.idf_vector = np.delete(self.idf_vector, cindex, 0)

    def freq_vector(self):
        f_vector = []
        for each in self.tokenizedEssays:
            count = [0] * len(bagofwords)
            for i in range(len(bagofwords)):
                for line in essay:
                    for word in line:
                        if word[0] in bagofwords:
                            index = bagofwords.index(word[0])
                            count[index] += 1
            f_vector.append(count)
        self.idf_vector = list(zip(i for i in f_vector))

