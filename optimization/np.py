import numpy as np

def initialisation(m, n):
    random_arr = np.random.randn(m, n)
    one_arr = np.ones((m, 1))
    result = np.concatenate((random_arr, one_arr), axis = 1, dtype="float16")
    print(result)

initialisation(4, 4)
initialisation(2, 4)