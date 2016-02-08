class Node(object):
    def __init__(self):
        self.count = 0
        self.child = {}


class Trie:
    def __init__(self):
        self.root = Node()

    def Insert(self, key):
        self.root = self.InsertAgain(self.root, key, 0)

    def InsertAgain(self, node, key, pos):
        if(pos == len(key)):
            node.count += 1
            return node
        if node.child.get(key[pos]) is None:
            node.child[key[pos]] = Node()
        node.child[key[pos]] = self.InsertAgain(node.child[key[pos]],
            key, pos+1)
        return node

    def Search(self, key):
        if(self.Count(key) > 0):
            return True
        return False

    def Count(self, key):
        return self.SearchAgain(self.root, key, 0)

    def SearchAgain(self, node, key, pos):
        if node is None:
            return 0
        if(pos == len(key)):
            return node.count
        if node.child.get(key[pos]) is None:
            return 0
        return self.SearchAgain(node.child[key[pos]], key, pos+1)

def main():
    data = ['pramod', 'uttam', 'navin', 'prabesh', 'pramod', 'pramodmjn']
    newTrie = Trie()
    for x in range(len(data)):
        newTrie.Insert(list(data[x]))
    print(newTrie.root.child.keys())
    nodep = newTrie.root.child['p']
    noder= nodep.child['r']
    nodea = noder.child['a']
    nodem = nodea.child['m']
    nodeo = nodem.child['o']
    noded = nodeo.child['d']
    print(noded.count)
    print(nodea.child.keys())
    print(newTrie.Search('pramod'))
    print(newTrie.Search(list('pamod')))
    print(newTrie.Search(list('saroj')))
    print(newTrie.Count('pramod'))
    print("No. of pramodmjn =",newTrie.Count('pramodmjn'))
if __name__=="__main__":
    main()



