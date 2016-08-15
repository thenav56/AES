import string
import math
import re
from trie import Trie
import numpy as np
import nltk
from nltk.corpus import stopwords

from cbfs import Cbfs
#import matplotlib.pyplot as plt

def Readfile(filename):
    vocabulary = []
    file = open(filename, "r", encoding="latin-1")
    for line in file:
        ngram = line.split()
        del ngram[0]
        vocabulary.append(ngram)
    return vocabulary

class Preprocess:
    def __init__(self):
        self.num_words = []
        self.num_sentences = []
        self.word_len = []
        self.sent_len = []
        self.gm_error = []
        self.num_stpwords= []
        self.num_verbs= []
        self.num_VBZVBG=[]
        self.rega = None
        self.regb = None #score = rega * error + regb

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

    def word_metrics(self, essays):
        for essay in essays:
            lines = re.split('[\.\?!]', essay)
            lines = [self.specialchar(i) for i in lines]
            num_sent = len(lines)
            num_word = 0
            num_char = 0
            stp = stopwords.words('english')
            num_stp = 0
            for line in lines:
                num_word += len(line)
                for word in line:
                    if word in stp:
                        num_stp += 1
                    num_char += len(word)
            sent_len = int(num_word/num_sent)
            word_len = int(num_char/num_word)
            self.num_words.append(num_word)
            self.num_sentences.append(num_sent)
            self.word_len.append(word_len)
            self.sent_len.append(sent_len)
            self.num_stpwords.append(num_stp/num_word)

    def tag_metrics(self, essays):
        for r, essay in enumerate(essays):
            lines = re.split('[\.\?!]', essay)
            lines = [self.specialchar(i) for i in lines]
            verb = 0
            vbz_vbg = 0
            for line in lines:
                tags = nltk.pos_tag(line)
                for tag in tags:
                    if tag[1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                        verb += 1
                for i in range(len(tags)-1):
                    if tags[i][1] == 'VBZ' and tags[i+1][1] == 'VBG':
                        vbz_vbg += 1
            self.num_verbs.append(verb)
            self.num_VBZVBG.append(vbz_vbg)

    
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

    def regression_coeff(self, x, y):
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
        b = (sumxy*sumx - sumy*sumx2)/(sumx**2 - n*sumx2)
        a = (sumy -n*b)/sumx
        self.rega = a
        self.regb = b

    
    def GetNgram(self, essays, nval):
        essay_ngram = []
        for essay in essays:
            Ngram = []
            lines = re.split('[\.\?!]', essay)
            lines = [self.specialchar(line) for line in lines]
            for line in lines:
                for i in range(len(line) - nval +1):
                    ngram = [line[i]]
                    for j in range(1,nval):
                        ngram.append(line[i+j])
                    Ngram.append(ngram)
            essay_ngram.append(Ngram)
        return essay_ngram

    def grammar_error(self, essays):
        essay_ngrams = self.GetNgram(essays, 2)
        tr = Trie(2)
        voc = Readfile("2gram.txt")
        for bigram in voc:
            tr.Insert(bigram)
        for essay in essay_ngrams:
            miss = 0
            for ngram in essay:
               miss += tr.Search(ngram)
            self.gm_error.append(miss/len(essay))


def main():
    from openpyxl import load_workbook
    wb = load_workbook('train.xlsx')
    ws = wb.active
    data = [[j.value for j in i] for i in ws]
    data = list(zip(*data))
    print(len(data[2]))
    essay = list(data[2][1:])
    score = list(data[6][1:])
    j = 0
    for i in range(len(score)):
        if(j>400):
            break
        if(score[i] == 8):
            del score[i]
            del essay[i]
            i -= 1
            j += 1

    scount = {}
    for each in score:
        scount[each] = scount.get(each,0)+1
    print(scount)
    train_len = 500
    train_essay = essay[:train_len]
    train_score = score[:train_len]
    pr = Preprocess()
    pr.word_metrics(essay)
    pr.tag_metrics(essay)
    vec = []
    vec.append(pr.num_words)
    vec.append(pr.num_verbs)
    vec.append(pr.num_sentences)
    bag = ['words', 'verbs', 'sentences']
    cb =Cbfs(bag, vec, score)
    cb.compute_rcf()
    cb.compute_rff()
    cb.ft_reduce(1)
    print(cb.bagofwords)

    #pr.grammar_error(essay)
    x = pr.num_words
    x = [i**(1/4.0) for i in x]
    print(pr.compute_correlation(x,score))
    print("sentence length:", pr.compute_correlation(pr.sent_len, score))
    print("word length:", pr.compute_correlation(pr.word_len, score))
    print("sentence count:", pr.compute_correlation(pr.num_sentences, score))
    print("word count:", pr.compute_correlation(pr.num_words, score))
    print("stopword count:", pr.compute_correlation(pr.num_stpwords, score))
    print("verb count:", pr.compute_correlation(pr.num_verbs, score))
    print("vbz-vbg:", pr.compute_correlation(pr.num_VBZVBG, score))
    print("word verb:", pr.compute_correlation(pr.num_words, pr.num_verbs))
    print("word sentence:", pr.compute_correlation(pr.num_words,
        pr.num_sentences))
    print("verb sentence:", pr.compute_correlation(pr.num_verbs,
        pr.num_sentences))
    #print("Gm error:", pr.compute_correlation(pr.gm_error, score))
    '''pr.regression_coeff(pr.gm_error[1:1300], score[1:1300])
    sc = score[1301:]
    gm = pr.gm_error[1301:]
    for i in range(len(sc)):
        print(sc[i],' :: ', pr.rega*gm[i]+pr.regb)
    '''

main()
