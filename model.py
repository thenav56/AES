from . import msvm
import pickle
import string
import math


def loadspellcorrector(dictfile):
    from .cspell.spell_corrector.cspell import cspell
    return cspell(dictfile)


class EssayModel:

    def __init__(self, dictfile="cspell/files/big.txt"):
        self.bagofwords = None
        self.idf_vector = None
        self.model = None
        self.essays = None
        self.train_vectors = None
        self.target = None
        self.dictfile = dictfile

    # essay is an essay(??)
    # returns an essay
    def preprocess(self, essay):
        r = []
        for i in essay:
            i = i.lower()
            if '@' not in i:
                t = ''.join(j for j in i if j in string.ascii_lowercase)
                r.append(t)
        return r

    # essay is list of essay
    def preprocess_set(self, essay):
        cp = loadspellcorrector(self.dictfile)  # spell corrector
        # correct minor spell errors using spell corrector
        allwords = set(j for i in essay for j in i)
        bword = {}
        for i in allwords:
            bword[i] = cp.best_word(i)
        essay = [[bword[j] for j in i] for i in essay]
        return essay

    # convert essay string into a dictionary
    def essaytodict(self, essay):
        dct = {}
        for j in essay:
            dct[j] = dct.get(j, 0) + 1
        return dct

    # "essays" is a list of essay
    # "scores" consists of the corresponding score of an essay in "essays"
    def train(self, essays, scores):
        # first remove named entities, punctuations, etc...
        essays = [self.preprocess(i) for i in essays]

        # now remove spell errors from whole set
        essays = self.preprocess_set(essays)
        essays = [self.essaytodict(i) for i in essays]
        # now obtain parameters(bags,idf) from the train set
        self.parameters_from_essays(essays)

        # now vectorize each essay string
        self.train_vectors = [self.vectorize(i) for i in essays]
        # now train the vectors using a classifier
        whole = list(zip(self.train_vectors, scores))
        print("training own")
        self.model = msvm.MSVM(whole)
        self.target = scores
        print("finished own")
        print('fitness:', self.model.score(self.train_vectors, scores))

    # vectorize an essay (list of words)
    def vectorize_raw(self, essay):
        return self.vectorize(self.essaytodict(self.preprocess(essay)))

    def score(self, essays, targets):
        t = 0
        for i, j in enumerate(essays):
            r = self.vectorize_raw(j)
            res = self.model.classify(r)
            t += targets[i] == res
            print('score ', targets[i], 'prediction', res, 'acc', t / (i + 1))

    # predict score of essays, essay is a list of words
    def predict(self, essays):
        return [self.model.classify(self.vectorize_raw(i)) for i in essays]

    def parameters_from_essays(self, essays):
        bagofwords = set()
        docfreq = {}
        for i in essays:
            for j in i:
                if j is not None:  # None is a major spell error
                    bagofwords.add(j)
                    docfreq[j] = docfreq.get(j, 0) + 1
        bagofwords = list(bagofwords)  # dimension
        idf_v = []  # idf vector
        for i in bagofwords:
            idf = math.log(len(essays) / (1 + docfreq[i]))
            idf_v.append(idf)

        self.idf_vector = idf_v
        self.bagofwords = bagofwords

    # essay is a dict word:count
    def vectorize(self, essay):
        v = []
        for r, i in enumerate(self.bagofwords):
            tf = essay.get(i, 0)
            v.append(tf * self.idf_vector[r])
        # v.append(essay.get(None, 0))  # incorrect spellings
        # length of essay in words
        # v.append(sum(i for _, i in essay.items())
        return v

    def dump(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)


def load_from_file(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model
