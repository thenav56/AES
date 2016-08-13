import msvm
import pickle
import string
import math
import numpy as np
import gensim
import kwrank
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def loadspellcorrector():
    dictfile = "cspell/files/big.txt"
    from cspell.spell_corrector.cspell import cspell
    return cspell(dictfile)

class EssayModel:

    def __init__(self):
        self.bagofwords = None
        self.idf_vector = None
        self.model = None
        self.essays = None
        self.train_vectors = None
        self.target = None
        self.svd = False
        self.spellCorr = loadspellcorrector()

    #"essays" is a list of essay
    #"scores" consists of the corresponding score of an essay in "essays"
    def sktrain(self):
        from sklearn import svm
        clf = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
        clf.fit(self.train_vectors, self.target)
        print('training set fit', clf.score(self.train_vectors, self.target))
        self.model = clf

    def score(self, essays, targets):
        acc = 0
        sum_a = 0
        sum_p = 0
        sum_aa = sum_pp = 0
        sum_ap = 0
        print('max scor', self.min_score, self.max_score)
        tot_dist = 0
        L = self.min_score
        U = self.max_score
        predict = {i : 0 for i in range(L, U + 1)}
        actual = {i : 0 for i in range(L, U + 1)}
        #running kappa calculator
        for i, j in enumerate(essays):
            v = self.lowSpace(self.vectorize(kwrank.filter(j, None)))
            p = self.model.predict([v])[0]
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
            kappa = 1 - dist_normalized / disagree
            print('test set fit %', jac * 100, 'actual', targets[i], 'predicted', p, 'kappa %', kappa * 100);

        n = len(essays)
        den = math.sqrt(n * sum_aa - sum_a * sum_a) * math.sqrt(n * sum_pp - sum_p * sum_p);
        if den:
            cor = (n * sum_ap - sum_a * sum_p) / den
            print('correlation', cor)

    def computeEigenVectors(self):
        import numpy as np
        from time import clock
        from scipy.linalg import eigh as largest_eigh
        from scipy.sparse.linalg.eigen.arpack import eigsh as largest_eigsh
        #Benchmark the sparse routine
        mat = np.array(self.train_vectors)
        mat = np.dot(mat.T, mat)
        start = clock()
        eva, self.evectors = largest_eigsh(mat, 20, which='LM')
        self.evectors = self.evectors.T
        elapsed = clock() - start
        print("svd time: ", elapsed)

    def lowSpace(self, data):
        if not self.svd:
            return data
        d = np.array(data)
        return [np.dot(d, j) for j in self.evectors]

    def train(self, essays, scores, min_score, max_score, sk):
        self.min_score = min_score
        self.max_score = max_score
        essays = [kwrank.filter(i, self.spellCorr) for i in essays]
        self.parameters_from_essays(essays)
        #print(self.bagofwords)
        #input('enter to continue...')
        #now vectorize each essay string
        self.train_vectors = [self.vectorize(i) for i in essays]
        if self.svd:
            self.computeEigenVectors()
            self.train_vectors = [self.lowSpace(i) for i in self.train_vectors]
        self.target = scores
        if sk:
            print("sk training start")
            self.sktrain()
            print("sk training finished")
            return
        #now train the vectors using a classifier
        whole = list(zip(self.train_vectors, scores))
        print("training own")
        self.model = msvm.MSVM(whole)
        print("finished own")
        #print('total bag ', len(self.bagofwords))
        #input('pause')
        #for i in self.bagofwords:
        #    print(i)
        #    input('')
        #print('fitness:', self.model.score(self.train_vectors, scores))
    
    #predict score of essays, essay is a list of words
    def predict(self, essays, sk = False): 
        v = [self.lowSpace(self.vectorize(kwrank.filter(i, None))) for i in essays]
        if sk:
            return self.model.predict(v)
        return [self.model.classify(i) for i in v]

    def parameters_from_essays(self, essays):
        approach = 2
        if approach == 1:
            #join sentences from all essays into a single array
            ns = [j for i in essays for j in i]
            self.bagofwords = kwrank.kwRank(ns)
        elif approach == 2:
            self.bagofwords = []
            ns = [kwrank.kwRank(i)[:20] for i in essays]
            for i in ns:
                self.bagofwords += i
            self.bagofwords = list(set(self.bagofwords))
            
    
    def essaytodict(self, essay):
        d = {}
        for sentence in essay:
            for word, tag in sentence:
                d[word] = d.get(word, 0) + 1
        return d
        
    #essay is of kwrank.filter return form
    def vectorize(self, essay):
        d = self.essaytodict(essay)
        return [float(d.get(i, 0)) for i in self.bagofwords]

    def dump(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

def load_from_file(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

