import numpy as np 

names = ['x values', 'cos(x)', 'sin(x)', 'exp(x)']
x = np.arange(0, 10, 0.1)
cosx = np.cos(x)
sinx = np.sin(x)
expx = np.exp(x)

np.savetxt("test.csv", np.c_[x, cosx, sinx, expx], delimiter=",", header=",".join(names)) 