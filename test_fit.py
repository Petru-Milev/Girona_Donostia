import numpy, scipy, matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import differential_evolution
import warnings

path = "Examples/Derivatives/Example6_Curve_Fit/data.csv"
matrix = numpy.loadtxt(path, delimiter=',', skiprows=1, dtype=str)

x = numpy.float64(matrix[:,3])
y = numpy.float64(matrix[:,4])

xData = numpy.array(x)
yData = numpy.array(y)


# Non-Linear Estimation Function
def func(V,a, b, c):
    return a + b*V + c*V**2


# function for genetic algorithm to minimize (sum of squared error)
def sumOfSquaredError(parameterTuple):
    warnings.filterwarnings("ignore") # do not print warnings by genetic algorithm
    val = func(xData, *parameterTuple)
    return numpy.sum((yData - val) ** 2.0)


def generate_Initial_Parameters():
    # min and max used for bounds
    maxX = max(xData)
    minX = min(xData)
    #maxY = max(yData)
    #minY = min(yData)

    parameterBounds = []
    parameterBounds.append([minX, maxX/100.0]) # search bounds for A
    parameterBounds.append([minX, maxX/100.0]) # search bounds for d

    # "seed" the numpy random number generator for repeatable results
    result = differential_evolution(sumOfSquaredError, parameterBounds, seed=3)
    return result.x

# by default, differential_evolution completes by calling curve_fit() using parameter bounds
geneticParameters = generate_Initial_Parameters()

# now call curve_fit without passing bounds from the genetic algorithm,
# just in case the best fit parameters are aoutside those bounds
fittedParameters, pcov = curve_fit(func, xData, yData, geneticParameters)
print('Fitted parameters:', fittedParameters)
print()