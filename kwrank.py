#!/bin/python
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from cspell.spell_corrector import cspell

def filter(essay, spellCorr):
    essay = ''.join([' ' if i == '/' else i for i in essay])
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

def kwRank(essay, window = 3, d = .85):
    debug = False
    r = essay
    if debug:
        for i in r:
            print(i)
        input()
    #maps word to id
    bagofwords = list(set(j[0] for i in r for j in i))
    N = len(bagofwords)
    word2id = {j : i for i, j in enumerate(bagofwords)}
    #maps id to edge list
    adjlist = {i : [] for i in range(N)}
    for i in r:
        for a, v1 in enumerate(i):
            for v2 in i[a + 1:a + 1 + window]:
                p, q = word2id[v1[0]], word2id[v2[0]]
                adjlist[p].append(q)
                adjlist[q].append(p)
    #maps id to score
    score = [1] * N
    while True:
        nscore = []
        for i in range(N):
            inscore = sum(score[j] / float(len(adjlist[j])) for j in adjlist[i])
            nscore.append((1.0 - d) + d * inscore)
        delta = sum(abs(nscore[i] - score[i]) for i in range(N))
        score = nscore
        if delta < 0.0001:
            break

    s = sorted(range(N), key = lambda i : score[i], reverse = True)
    ranked = [bagofwords[i] for i in s]
    return ranked

def main():
    essay = """
Dear local newspaper, I think effects computers have on people are great learning skills/affects because they give us time to chat with friends/new people, helps us learn about the globe(astronomy) and keeps us out of troble! Thing about! Dont you think so? How would you feel if your teenager is always on the phone with friends! Do you ever time to chat with your friends or buisness partner about things. Well now - there's a new way to chat the computer, theirs plenty of sites on the internet to do so: @ORGANIZATION1, @ORGANIZATION2, @CAPS1, facebook, myspace ect. Just think now while your setting up meeting with your boss on the computer, your teenager is having fun on the phone not rushing to get off cause you want to use it. How did you learn about other countrys/states outside of yours? Well I have by computer/internet, it's a new way to learn about what going on in our time! You might think your child spends a lot of time on the computer, but ask them so question about the economy, sea floor spreading or even about the @DATE1's you'll be surprise at how much he/she knows. Believe it or not the computer is much interesting then in class all day reading out of books. If your child is home on your computer or at a local library, it's better than being out with friends being fresh, or being perpressured to doing something they know isnt right. You might not know where your child is, @CAPS2 forbidde in a hospital bed because of a drive-by. Rather than your child on the computer learning, chatting or just playing games, safe and sound in your home or community place. Now I hope you have reached a point to understand and agree with me, because computers can have great effects on you or child because it gives us time to chat with friends/new people, helps us learn about the globe and believe or not keeps us out of troble. Thank you for listening.
Dear reader, @ORGANIZATION1 has had a dramatic effect on human life. It has changed the way we do almost everything today. The most well know, is the computer. This device has allowed people do buy things online, talk to people online, and also provides entertainment for some people. All good qualities that make everyones lives easier. Imagine you look into your refrigerator and you notice it's almost empty. Someone is using the car and you need to go grocery shopping and the store is too far. What do you do? Well you could go on a computer and look for food online. Ther are many great deals and some companies even deliver for free! The amazing and easy way to buy food without leaving your house. But food isn't all you can purchase. Many products are sold through the computer. Need new toys for kids? Or how about a new hat for your friend? Maybe even more curtains for your room? Well at the easy access of internet on a computer, you can buy all those items and more. The computer has also the way of communication. Let's say someone wants to talk to a friend or relative that lives far away in another country. @CAPS1 someone dosen't own a phone or @CAPS1 they can't make the call, all these is to be in you on the computer. You can communicate with anyone just by using your email adress. Now friends and families can talk to each other over the ease of the computer. Just type to want to say and "boom," instant, on the chat. Let's face it. No matter what a child or even teenager . But now with a computer all that can change. With just one click you could actually be watching a movie from the comfort of your own home. But what @CAPS1 you don't want a movie? No entertainment like listing to musics, watching fun, and probable the most popular playing games. Everyone loves to play a game every once in a while, and with the selection of thousands of online games, these isn't or person who can't fled atleast our game enjoyable. There are even games for educational fun that many kids love. With all the entertainment a computer can produce; who could hate it? All in all the computer is a revolutinizing device that has changes the way we shop, communicate, and find exciting entertainment. To be able to do so much with just a couple clicks; new that I find extravagant. It blows my mind to see and think, "@CAPS1 we can do this now, I wonder what we can accomplish in the future.
Dear local newspaper I raed ur argument on the computers and I think they are a positive effect on people. The first reson I think they are a good effect is because you can do so much with them like if you live in mane and ur cuzin lives in califan you and him could have a wed chat. The second thing you could do is look up news any were in the world you could be stuck on a plane and it would be vary boring when you can take but ur computer and go on ur computer at work and start doing work. When you said it takes away from exirsis well some people use the computer for that too to chart how fast they run or how meny miles they want and sometimes what they eat. The thrid reson is some peolpe jobs are on the computers or making computers for exmple when you made this artical you didnt use a type writer you used a computer and printed it out if we didnt have computers it would make ur @CAPS1 a lot harder. Thank you for reading and whe you are thinking adout it agen pleas consiter my thrie resons.
    """
    dictfile = "cspell/files/big.txt"
    sc = cspell(dictfile)
    r = filter(essay, sc)
    print(kwRank(r))

if __name__ == '__main__':
    main()
