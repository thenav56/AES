
import sys, getopt
from trie import Trie

def Readfile(filename):
    vocabulary = []
    file = open(filename, "r", encoding="latin-1")
    for line in file:
        ngram = line.split()
        del ngram[0]
        vocabulary.append(ngram)
    return vocabulary


class Preprocess:
    def __init__(self, val):
        self.text = val
        self.unigram = []
        self.bigram = []
        self.trigram = []
        self.words = []
        self.Getwords()

    def Getwords(self):
        sent = self.text.lower().split(".")
        del sent[-1]
        for i in range(len(sent)):
            line = sent[i].replace(",", "").replace("'", "")
            twords = line.split()
            self.words.extend(twords)
            self.unigram.extend(self.GetNgram(twords, 1))
            self.bigram.extend(self.GetNgram(twords, 2))
            self.trigram.extend(self.GetNgram(twords, 3))


    def GetNgram(self, twords, nval):
        Ngram = []
        for i in range(len(twords) - nval+1):
            ngram = [twords[i]]
            for j in range(1,nval):
                ngram.append(twords[i+j])
            Ngram.append(ngram)
        return Ngram

    def CountWords(self):
        return len(self.words)

    def CountBigram(self):
        return len(self.bigram)

    def CountTrigram(self):
        return len(self.trigram)
            


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print('test.py -i <inputfile>')
            sys.exit(2)
        if opt in ("-i", "--ifile"):
            filename = arg
    content = open(filename).read()
    sentence = Preprocess(content)
   
    vocabulary = Readfile("3gram.txt")
    tritree = Trie(3)
    for ngram in vocabulary:
        tritree.Insert(ngram)


    print(sentence.words)
    print(sentence.CountWords())
    print(sentence.CountTrigram())
    
    hit = 0
    miss = 0
    for tri in sentence.trigram:
        if(tritree.Search(tri)):
            hit += 1
        else:
            miss += 1

    print(hit," ", miss)

    '''words = Getwords(examp)
    print words
    print len(words)
    bigram = Ngram(3)
    bigram.GetNgram(words)
    print Ngram.NgramList
'''
if __name__=="__main__":
    main(sys.argv[1:])

