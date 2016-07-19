import ctypes
import numpy as np

class BSVM:

    def __init__(self):
        self.data = None
        self.target = None
        self.alpha = None
        self.b = None

    def kernel(self, a, b):
        return np.dot(a, b)
        return (np.dot(a, b) + 1) ** 2

    def classify(self, x):
        r = 0
        for i in range(len(self.data)):
            r += self.alpha[i] * self.target[i] * self.kernel(self.data[i], x)
        return 1 if r - self.b >= 0 else -1

    #self.data will contain only support vectors after the training
    def train(self, data, target):
        test = ctypes.CDLL("./smo/lsmo.so")
        #FUNCTION PARAMETERS
        test.solve.argtypes = [
            ctypes.POINTER(ctypes.c_float), 
            ctypes.POINTER(ctypes.c_float), 
            ctypes.POINTER(ctypes.c_float), 
            ctypes.POINTER(ctypes.c_float), 
            ctypes.c_int, 
            ctypes.c_int,
        ]

        #FUNCTION RETURN TYPE
        test.solve.restype = ctypes.c_float

        #FLATTEN TRAINING SET
        train_set = [j for i in data for j in i]
        N = len(target)
        numfeatures = len(data[0])
        
        train_c = (ctypes.c_float * len(train_set))(*train_set)
        target_c = (ctypes.c_float * N)(*target)
        alpha = (ctypes.c_float * N)(*target)
        error_cache = (ctypes.c_float * N)(*target)

        self.b = test.solve(train_c, target_c, alpha, error_cache, ctypes.c_int(N), ctypes.c_int(numfeatures))
        self.alpha = []
        self.data = []
        self.target = []
        for i, j in enumerate(alpha):
            if j > 0:
                self.alpha.append(j)
                self.data.append(data[i])
                self.target.append(target[i])
        print('org size', len(alpha), 'new size', len(self.alpha))

    def score(self, data, target, pr = False):
        r = 0
        for i, d in enumerate(data):
            cr = self.classify(d)
            r += target[i] == cr
            if pr:
                print('running', r / (i + 1))
        return r / len(data)

