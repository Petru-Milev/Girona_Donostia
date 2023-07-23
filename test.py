import numpy as np 

a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
a = np.array((a))
a = np.float128(a)
print(type(a[1][1]))