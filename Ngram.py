def Getwords(essay):
    list = essay.split()
    return list

class Preprocess:
    def __init__(self, val):
        self.text = val
        self.unigram = []
        self.bigram = []
        self.trigram = []
        self.words = []

    def Getwords(self):
        self.sent = self.text.lower().split(".")
        del self.sent[-1]
        for i in range(len(self.sent)):
            line = self.sent[i].split()
            self.words.extend(line)
            self.unigram.extend(self.GetNgram(line, 1))
            self.bigram.extend(self.GetNgram(line, 2))
            self.trigram.extend(self.GetNgram(line, 3))


    def GetNgram(self, twords, nval):
        Ngram = []
        for i in range(len(twords) - nval+1):
            ngram = [twords[i]]
            for j in range(1,nval):
                ngram.append(twords[i+j])
            Ngram.append(ngram)
        return Ngram
            


def main():
    examp = "Hi my name is pramod maharjan. I am in bad mood."
    sentence = Preprocess(examp)
    sentence.Getwords()
    print(sentence.sent)
    print(sentence.words)
    print(sentence.unigram)
    print(sentence.bigram)
    print(sentence.trigram)

    '''words = Getwords(examp)
    print words
    print len(words)
    bigram = Ngram(3)
    bigram.GetNgram(words)
    print Ngram.NgramList
'''
if __name__=="__main__":
    main()

