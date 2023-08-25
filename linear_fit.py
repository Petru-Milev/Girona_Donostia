import numpy as np
from scipy.optimize import curve_fit


def func_fit(vect_x, vect_y, order):

    if isinstance(vect_x, np.float64):
        None
    else: 
        vect_x = np.float64(vect_x)
    if isinstance(vect_y, np.float64):
        None
    else:
        vect_y = np.float64(vect_y)
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
    polynomials_that_can_be_fitted = ["1", "2", "3", "4", "5", "6"]
    test_parameters = False
    if order in polynomials_that_can_be_fitted:
        test_parameters = np.polynomial.polynomial.polyfit(vect_x, vect_y, int(order))

    map_func = {"1" : func1, "2" : func2, "3" : func3, "4" : func4, "5" : func5, "6" : func6, "test1" : test1}
    func = map_func[order]
    if isinstance(test_parameters, np.ndarray):
        popt, pconv = curve_fit(func, vect_x, vect_y, p0 = test_parameters)
    else:
        popt, pconv = curve_fit(func, vect_x, vect_y)
    return popt, pconv


def add_data_from_linear_fit(matrix, vector_x, coef):
    if isinstance(vector_x, np.longdouble):
        None
    else:
        vector_x = np.longdouble(vector_x)
    if isinstance(coef, np.longdouble):
        None
    else:
        coef = np.longdouble(coef)

    """
    This function will add to matrix, a new column with vector_x multiplied by coef.
    """
    def func(x, coef):
        sum_1 = 0
        for index, elem in enumerate(coef):
            sum_1 += elem * (x ** (index))
        return sum_1
    #func = np.vectorize(func, excluded = ["coef"])
    vector_y = func(vector_x, coef)
    matrix = np.column_stack((matrix, vector_y))
    return matrix 


#path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example1/data_from_folder_Example1.csv"
path = "Examples/Derivatives/Example6_Curve_Fit/data.csv"
matrix = np.loadtxt(path, delimiter=',', skiprows=1, dtype=str)
#print(matrix.shape)
#print(matrix[:,3].shape)

left = np.float64(matrix[:,3])
right = np.float64(matrix[:,4])

#A = func_fit(left, right, "np_2")
#print(A)

A = func_fit(left, right, 2)
print(f"popt is {A[0]}")