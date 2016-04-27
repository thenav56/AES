import ctypes
import numpy as np

class BSVM:

    def __init__(self, data, target):
        self.data = data
        self.target = target
        self.build()

    def kernel(self, a, b):
        return np.dot(a, b)
        return (np.dot(a, b) + 1) ** 2

    def classify(self, x):
        r = 0
        for i in range(len(self.data)):
            if self.alpha[i] > 0:
                r += self.alpha[i] * self.target[i] * self.kernel(self.data[i], x)
        return 1 if r - self.b >= 0 else -1

    def build(self):
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
        train_set = [j for i in self.data for j in i]
        N = len(self.target)
        numfeatures = len(self.data[0])
        
        train_c = (ctypes.c_float * len(train_set))(*train_set)
        target_c = (ctypes.c_float * N)(*self.target)
        alpha = (ctypes.c_float * N)(*self.target)
        error_cache = (ctypes.c_float * N)(*self.target)
        self.b = test.solve(train_c, target_c, alpha, error_cache, ctypes.c_int(N), ctypes.c_int(numfeatures))

        self.alpha = [i for i in alpha]
        #print(self.alpha)
