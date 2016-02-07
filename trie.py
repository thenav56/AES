class Node(object):
    count = 0
    child = {}


class Trie:
    def __init__(self):
        self.root = Node()

    def Insert(self, key):
        self.root = self.InsertAgain(self.root, key, 0)

    def InsertAgain(self, node, key, pos):
        if node is None:
            node = Node()
        if(pos == len(key)):
            node.count += 1
            return node
        node.child[key[pos]] = Node()
        node.child[key[pos]] = self.InsertAgain(node.child[key[pos]],
            key, pos+1)
        return node

    def Search(self, key):
        return self.SearchAgain(self.root, key, 0)

    def SearchAgain(self, node, key, pos):
        if node is None:
            return False
        if(pos == len(key)):
            if(node.count > 0):
                return True
            return False
        default = Node()
        if node.child.get(key[pos], default) is None:
            return False
        return self.SearchAgain(node.child[key[pos]], key, pos+1)

def main():
    data = ['pramod', 'uttam', 'navin', 'prabesh']
    newTrie = Trie()
    for x in range(len(data)):
        newTrie.Insert(list(data[x]))
    print newTrie.Search('pramod')
    #print newTrie.Search(list('palme'))

if __name__=="__main__":
    main()



