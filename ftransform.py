import pickle
import string
import math
import numpy as np
import kwrank
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def loadspellcorrector():
    dictfile = "cspell/files/big.txt"
    from cspell.spell_corrector.cspell import cspell
    return cspell(dictfile)

class BaseFeatureTransform:
    def __init__(self):
        self.data_set = None
        self.tokenized = None
        self.bagofwords = None
        self.spellCorr = loadspellcorrector()

    def setDataSet(self, data_set):
        self.data_set = data_set
        self.parameters_from_essays()
        self.tokenized = [self.tokenizeEssay(i) for i in self.data_set]

    def getTransformed(self, essays, corr = False):
        return [self.vectorize(self.refine(
            self.tokenizeEssay(i, None if not corr else self.spellCorr)
            )) for i in essays]

    def tokenizeEssay(self, essay, spellCorr = None):
        essay = ''.join(['or' if i == '/' else i for i in essay])
        r = nltk.sent_tokenize(essay)
        r = [nltk.word_tokenize(i) for i in r]
        r = [nltk.pos_tag(i) for i in r]
        if spellCorr != None:
            nr = []
            for i in r:
                s = []
                for j in i:
                    s.append([spellCorr.best_word(j[0].lower()), j[1]])
                nr.append(s)
            r = nr
        return r

    def refine(self, essay):
        r = essay
        r = [[j for j in i if j[0] != None and j[0][0] in string.ascii_lowercase] for i in r] 
        nr = []
        lm = WordNetLemmatizer()
        for i in r:
            s = []
            for j in i:
                w = j[0]
                tag = j[1]
                if 'NN' in tag[:2]:
                    w = lm.lemmatize(w, 'n')
                elif 'VB' in tag[:2]:
                    w = lm.lemmatize(w, 'v')
                s.append([w, tag])
            nr.append(s)
        r = nr
        stp = stopwords.words('english')
        r = [[j for j in i if j[0].lower() not in stp] for i in r] 
        #remove useless words   
        pt = ['PRP', 'WRB', 'PRP$', 'MD', 'NNP', 'CC', 'IN', 'VBZ', 'WP$']
        r = [[j for j in i if j[1] not in pt] for i in r]
        return r

    def parameters_from_essays(self):
        s = [self.refine(self.tokenizeEssay(i, self.spellCorr)) for i in self.data_set]
        approach = 2
        if approach == 1:
            #join sentences from all essays into a single array
            ns = [j for i in s for j in i]
            self.bagofwords = kwrank.kwRank(ns)[:2000]
        elif approach == 2:
            self.bagofwords = []
            ns = [kwrank.kwRank(i)[:20] for i in s]
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
    def vectorize(self, essay_1):
        d = self.essaytodict(essay)
        return [float(d.get(i, 0)) for i in self.bagofwords]

class SVDFeatureTransform(BaseFeatureTransform):
    def __init__(self):
        pass

    def pipeline(self):
        self.parameters_from_essays()

    def parameters_from_essays(self, essays):
        #parent.parameters_from_essays()
        #fkfjasjf
        pass

class PasaMod(BaseFeatureTransform): 
    def refine(self):
        #parent.refine()
        #yours
        pass
