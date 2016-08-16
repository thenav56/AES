import math
import nltk
import numpy as np
from ftransform import BaseFeatureTransform
import time
from cspell.spell_corrector import cspell
from grammar.trie import Trie
import re
import string
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def Readfile(filename):
    vocabulary = []
    file = open(filename, "r", encoding="latin-1")
    for line in file:
        ngram = line.split()
        del ngram[0]
        vocabulary.append(ngram)
    return vocabulary

class Cbfs(BaseFeatureTransform):
    def __init__(self):
        super(Cbfs, self).__init__()
        self.idf_vector = None
        self.trie = Trie(2)
        self.cspell = cspell(os.path.join(BASE_DIR,
                            './cspell/files/wordcount.txt'))
        #may need to calculate the transpose
        self.rff = None
        self.rcf = None

    #initiate a matrix of zeros
    def autofn(self):
        n = len(self.bagofwords)
        self.rff = np.zeros((n,n), dtype=float)
        voc = Readfile("2gram.txt")
        for ngram in voc:
            self.trie.Insert(ngram)
        

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
        den = math.sqrt(sxx*syy) 
        if( den == 0):
            r = 0
        else:
            r = sxy/math.sqrt(sxx*syy)
        return r

    def corr(self, sx, sy, sxy, sxx, syy, n):
        sxx= n*sxx - sx * sx
        syy = n*syy - sy * sy
        sxy = n*sxy - sx * sy
        den = math.sqrt(sxx*syy) 
        if( den == 0):
            r = 0
        else:
            r = sxy/math.sqrt(sxx*syy)
        return r

    #feature-feature correlation
    def compute_rff(self):
        M = np.array(self.idf_vector)
        cov = np.dot(M, M.T)
        summ = [0] * len(self.bagofwords)
        sqsum = [0] * len(self.bagofwords)
        for i in range(len(self.bagofwords)):
            for j in self.idf_vector[i]:
                summ[i] += j
                sqsum[i] += j * j
        for i in range(len(self.bagofwords)):
            for j in range(i+1, len(self.bagofwords)):
                n = len(self.idf_vector[0])
                self.rff[i][j] = self.corr(summ[i], summ[j], cov[i][j], sqsum[i], sqsum[j], n)

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
        calc = {}
        bg = set(self.bagofwords)
        for essay in self.tokenized:
            count = [0] * len(self.bagofwords)
            for line in essay:
                for word in line:
                    if word[0] in bg:
                        if word[0] not in calc:
                            calc[word[0]] = self.bagofwords.index(word[0])
                        index = calc[word[0]]
                        count[index] += 1
            f_vector.append(count)
        self.idf_vector = list(map(list,zip(*f_vector)))
    
    def parameters_from_essays(self):
        super(Cbfs, self).parameters_from_essays()
        self.autofn()
        
        t = time.time()
        print('freq start')
        self.freq_vector()
        print('freq finish')
        self.compute_rcf()
        self.compute_rff()
        print(time.time() -t)
        print("length of bagofwords",len(self.bagofwords))
        self.ft_reduce(50)
        print("length of reduced bagofwords", len(self.bagofwords))
        print(time.time() - t)
        input()

    def word_count(self, essay):
        lines = nltk.sent_tokenize(essay)
        lines = [nltk.word_tokenize(i) for i in lines]
        num_word = 0
        for line in lines:
            num_word += len(line)
        return num_word
        #self.num_words.append(num_word)

    def specialchar(self, essay):
        line = essay.split() #split into words
        r = []
        for i in line:
            i = i.lower()
            if '@' not in i:
                t = ''.join(j for j in i if j in string.ascii_lowercase)
                if t !='':
                    r.append(t)
        return r

    def spell_count(self, essay):
        removal = [',','.','?','@','!']
        rx = '['+re.escape(''.join(removal))+']'
        refined_essay = re.sub(rx, '', essay)

        wrong_count = 0
        total_word = 1
        for line in refined_essay.splitlines():
            for word in line:
                total_word += 1
                if not self.cspell.check(word, correct=False):
                    wrong_count += 1
        return wrong_count*1.0/total_word


    def GetNgram(self, essay, nval):
            essay_ngram = []
            lines = re.split('[\.\?!]', essay)
            lines = [self.specialchar(line) for line in lines]
            for line in lines:
                for i in range(len(line) - nval +1):
                    ngram = [line[i]]
                    for j in range(1,nval):
                        ngram.append(line[i+j])
                    essay_ngram.append(ngram)
            return essay_ngram

    def grammar_count(self, essay):
        essay_ngram = self.GetNgram(essay, 2)
        miss = 0
        for each in essay_ngram:
            miss += 1 - self.trie.Search(each)
        if(len(essay_ngram)):
            return miss*1.0/len(essay_ngram)
        else:
            return 0

    def getTransformed(self, essays, corr = False):
        v = super(Cbfs, self).getTransformed(essays, corr)
        t_vec = []
        for pos, i in enumerate(v):
            a = []
            wc = self.word_count(essays[pos])
            #normalize term frequency
            for j in range(len(i)):
                i[j] = i[j]
            a.append(self.grammar_count(essays[pos]))
            a.append(self.spell_count(essays[pos]))
            #a.append(wc)
            i.extend(a)
        return v

