class Node(object):
    def __init__(self):
        self.count = 0
        self.child = {}
        self.nextRoot = None


class Trie:
    def __init__(self, n):
        self.ngram = n
        self.root = Node()

    def Insert(self, key):
        self.root = self.InsertAgain(self.root, key, 0, 0)

    def InsertAgain(self, node, key, wpos, lpos):
        if(lpos == len(key[wpos])):
            if(wpos == self.ngram-1):
                node.count += 1
                return node
            else:
                if node.nextRoot is None:
                    node.nextRoot = Node()
                node.nextRoot = self.InsertAgain(node.nextRoot, key, wpos+1, 0)
                return node
        index = key[wpos][lpos]
        if node.child.get(index) is None:
            node.child[index] = Node()
        node.child[index] = self.InsertAgain(node.child[index],
            key, wpos, lpos+1)
        return node

    def Search(self, key):
        if(self.Count(key) > 0):
            return True
        return False

    def Count(self, key):
        return self.SearchAgain(self.root, key, 0, 0)

    def SearchAgain(self, node, key, wpos, lpos):
        if node is None:
            return 0
        if(lpos == len(key[wpos])):
            if(wpos == self.ngram-1):
                return node.count
            else:
                if node.nextRoot is None:
                    return 0
                return self.SearchAgain(node.nextRoot, key, wpos+1, 0)
        index = key[wpos][lpos]
        if node.child.get(index) is None:
            return 0
        return self.SearchAgain(node.child[index], key, wpos, lpos+1)

def Readfile(filename):
    vocabulary = []
    file = open(filename, "r", encoding="latin-1")
    for line in file:
        ngram = line.split()
        del ngram[0]
        vocabulary.append(ngram)
    return vocabulary

def main():
    vocabulary = Readfile("3gram.txt")
    tritree = Trie(3)
    for ngram in vocabulary:
        tritree.Insert(ngram)

    #print(tritree.Search(['the', 'world', 'is']))
    #data = ['pramod', 'uttam', 'navin', 'prabesh', 'pramod', 'pramodmjn']
    newTrie = Trie(2)
    newTrie.Insert(['my', 'project'])
    newTrie.Insert(['my', 'name'])
    newTrie.Insert(['your', 'project'])
    newTrie.Insert(['your', 'name'])
    newTrie.Insert(['my', 'project'])
    print(newTrie.root.child.keys())

    print(newTrie.Search(['my', 'name']))
    print(newTrie.Search(['my', 'project']))
    print(newTrie.Search(['my', 'Project']))
    print(newTrie.Count(['my', 'project']))

    oneGram = Trie(1)
    oneGram.Insert(['pramod'])
    oneGram.Insert(['navin'])
    oneGram.Insert(['uttam'])
    oneGram.Insert(['prabesh'])
    oneGram.Insert(['pramod'])
    print(oneGram.Search(['pramod']))
    print(oneGram.Search(['teskabaje']))
    print(oneGram.Count(['pramod']))
    print(oneGram.Count(['prabesh']))
if __name__=="__main__":
    main()



