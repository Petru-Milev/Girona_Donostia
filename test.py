import numpy as np

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


coef = [1.6337107717558903, -366.0034827446434, 994.7074745991632]

path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example6_Curve_Fit/data.csv"
matrix = np.loadtxt(path, delimiter=',', skiprows=1, dtype=str)
vector_x = matrix[:,3]
print(f"initial matrix shape: {matrix.shape}")
A = add_data_from_linear_fit(matrix, vector_x, coef)
#print(A)
print(f"final matrix shape: {A.shape}")
np.savetxt("test.csv", A, delimiter=",", fmt="%s")