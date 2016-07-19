import msvm
import pickle
import string
import math
import numpy as np
import gensim
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def loadspellcorrector():
    dictfile = "cspell/files/big.txt"
    import importlib.util
    spec = importlib.util.spec_from_file_location("cspell", "cspell/spell_corrector/cspell.py")
    cs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cs)
    return cs.cspell(dictfile)

class EssayModel:

    def __init__(self):
        self.bagofwords = None
        self.idf_vector = None
        self.model = None
        self.essays = None
        self.train_vectors = None
        self.target = None

    #essay is an essay(??)
    #returns an essay
    def preprocess(self, essay):
        r = []
        for i in essay:
            i = i.lower()
            if '@' not in i:
                t = ''.join(j for j in i if j in string.ascii_lowercase)
                r.append(t)
        return r

    #essay is list of essay
    @staticmethod
    def preprocess_set(essay):
        #cp = loadspellcorrector()#spell corrector
        #correct minor spell errors using spell corrector
        allwords = set(j for i in essay for j in i)
        bword = {}
        for i in allwords:
            #bword[i] = cp.best_word(i)
            bword[i] = i
        essay = [[bword[j] for j in i] for i in essay]
        return essay

    #convert essay string into a dictionary
    @staticmethod
    def essaytodict(essay):
        dct = {}
        for j in essay:
            dct[j] = dct.get(j, 0) + 1
        return dct

    #"essays" is a list of essay
    #"scores" consists of the corresponding score of an essay in "essays"
    def sktrain(self):
        from sklearn import svm
        clf = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
        clf.fit(self.train_vectors, self.target)
        print('training set fit', clf.score(self.train_vectors, self.target))
        self.model = clf

    def skscore(self, vectors, targets):
        vectors = [self.lowSpace(self.vectorize_raw(i)) for i in
                vectors]
        print('test set fit', self.model.score(vectors, targets))

    def computeEigenVectors(self):
        import numpy as np
        from time import clock
        from scipy.linalg import eigh as largest_eigh
        from scipy.sparse.linalg.eigen.arpack import eigsh as largest_eigsh
        #Benchmark the sparse routine
        mat = np.array(self.train_vectors)
        mat = np.dot(mat.T, mat)
        start = clock()
        eva, self.evectors = largest_eigsh(mat, 200, which='LM')
        self.evectors = self.evectors.T
        elapsed = clock() - start
        print("svd time: ", elapsed)

    def lowSpace(self, data):
        d = np.array(data)
        return [np.dot(d, j) for j in self.evectors]

    def train(self, essays, scores, sk = False):
        #first remove named entities, punctuations, etc...
        essays = [self.preprocess(i) for i in essays]
        stp = stopwords.words('english')
        lm = WordNetLemmatizer()
        essays = [[lm.lemmatize(j) for j in i if j not in stp] for i in essays]

        #now remove spell errors from whole set
        essays = EssayModel.preprocess_set(essays)
        essays = [EssayModel.essaytodict(i) for i in essays]
        #now obtain parameters(bags,idf) from the train set
        self.parameters_from_essays(essays)

        #now vectorize each essay string
        self.train_vectors = [self.vectorize(i) for i in essays]
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
        print('total bag ', len(self.bagofwords))
        input('pause')
        #for i in self.bagofwords:
        #    print(i)
        #    input('')
        #print('fitness:', self.model.score(self.train_vectors, scores))
    
    #vectorize an essay (list of words)
    def vectorize_raw(self, essay):
        return self.vectorize(self.essaytodict(self.preprocess(essay)))

    def score(self, essays, targets):
        t = 0
        for i, j in enumerate(essays):
            r = self.lowSpace(self.vectorize_raw(j))
            res = self.model.classify(np.array(r))
            t += targets[i] == res
            print('score ', targets[i], 'prediction', res, 'acc', t * 1.0 / (i + 1))

    #predict score of essays, essay is a list of words
    def predict(self, essays, sk = False): 
        v = [self.lowSpace(self.vectorize_raw(i)) for i in essays]
        if sk:
            return self.model.predict(v)
        return [self.model.classify(i) for i in v]

    def parameters_from_essays(self, essays):
        bagofwords = set()
        docfreq = {}
        for i in essays:
            for j in i:
                if j != None: #None is a major spell error
                    bagofwords.add(j)
                    docfreq[j] = docfreq.get(j, 0) + 1
        bagofwords = list(bagofwords) #dimension
        #bgw = mlda(train_essay)

        idf_v = []#idf vector
        for i in bagofwords:
            idf = math.log(len(essays) / (1 + docfreq[i]))
            idf_v.append(idf)

        self.idf_vector = idf_v
        self.bagofwords = bagofwords

    #essay is a dict word:count
    def vectorize(self, essay):
        v = []
        for r, i in enumerate(self.bagofwords):
            tf = essay.get(i, 0)
            v.append(tf * self.idf_vector[r])
        errors = essay.get(None, 0)
        for i in essay:
            if i not in self.bagofwords:
                errors += essay[i]
        v.append(errors)#incorrect spellings
        #v.append(sum(i for _, i in essay.items())) #length of essay in words
        return v

    def dump(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

def load_from_file(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

