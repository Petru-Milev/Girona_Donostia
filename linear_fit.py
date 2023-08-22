import numpy as np
from scipy.optimize import curve_fit


def func_fit(x, y, order):
    def func1(x, a, b):
        return a + b*x

    def func2(x, a, b, c):
        return a + b*x + c*x**2

    def func3(x, a, b, c, d):
        return a + b*x + c*x**2 + d*x**3

    def func4(x, a, b, c, d, e):
        return a + b*x + c*x**2 + d*x**3 + e*x**4

    def func5(x, a, b, c, d, e, f):
        return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5

    def func6(x, a, b, c, d, e, f, g):
        return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6

    def test1(x, a, b, c, s1, s2, c1, c2 ):
        return a + b*x + c*x**2 + s1*np.sin(s2*x) + c1*np.cos(c2*x)
    
    def polynomial_fit(x,y, n):
        result = np.polynomial.polynomial.polyfit(x, y, n)
        return result
    
    order = str(order)
    if "np" in order.split("_"):
        order = order.split("_")
        order = int(order[1])
        return polynomial_fit(x, y, order)
    
    map_func = {"1" : func1, "2" : func2, "3" : func3, "4" : func4, "5" : func5, "6" : func6, "test1" : test1}
    func = map_func[order]
    popt, pconv= curve_fit(func, x, y)
    return popt, pconv



#path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example1/data_from_folder_Example1.csv"
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/wB97X_c_ultrafine.csv"
matrix = np.loadtxt(path, delimiter=',', skiprows=1, dtype=str)
print(matrix.shape)
print(matrix[:,3].shape)

left = np.float64(matrix[:,3])
right = np.float64(matrix[:,4])

#A = polynomial_fit(left, right, 2)
#print(A)


