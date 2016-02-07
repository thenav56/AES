def Getwords(essay):
    list = essay.split()
    return list

class Ngram:
    Nvalue = 1
    NgramList = {}
    def __init__(self, val):
        Ngram.nvalue = val

    def GetNgram(self, list):
        for i in range(len(list)-Ngram.nvalue+1):
            ngram = list[i]
            for j in range(1,Ngram.nvalue):
                ngram = ngram+" "+list[i+j]
            Ngram.NgramList[i] = ngram

def main():
    examp = "Hi my name is pramod maharjan."
    words = Getwords(examp)
    print words
    print len(words)
    bigram = Ngram(3)
    bigram.GetNgram(words)
    print Ngram.NgramList

if __name__=="__main__":
    main()

