import numpy, scipy, matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import differential_evolution
import warnings

x = [0.00, 27.01,84.15,134.66,178.74,217.00,250.20,279.06,304.24, 
                  326.29,346.71,362.87,378.13,391.75,403.96,414.96]

y = [0.00,440.00,933.00,1154.00,1226.00,1222.00,1185.00,
                 1134.00,1081.00,1031.00,984.00,942.00,904.00,870.00,840.00,814.00]

xData = numpy.array(x, dtype=float)
yData = numpy.array(y, dtype=float)


# Non-Linear Estimation Function
def func(V,A,d):
    return A*V*numpy.exp(-1.0*d*V)


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
    parameterBounds.append([minX, maxX/10.0]) # search bounds for A
    parameterBounds.append([minX, maxX/10.0]) # search bounds for d

    # "seed" the numpy random number generator for repeatable results
    result = differential_evolution(sumOfSquaredError, parameterBounds, seed=3)
    print(f"result.x: {result}")
    return result.x

# by default, differential_evolution completes by calling curve_fit() using parameter bounds
geneticParameters = generate_Initial_Parameters()

# now call curve_fit without passing bounds from the genetic algorithm,
# just in case the best fit parameters are aoutside those bounds
fittedParameters, pcov = curve_fit(func, xData, yData, geneticParameters)
print('Fitted parameters:', fittedParameters)
print()

modelPredictions = func(xData, *fittedParameters) 

absError = modelPredictions - yData

SE = numpy.square(absError) # squared errors
MSE = numpy.mean(SE) # mean squared errors
RMSE = numpy.sqrt(MSE) # Root Mean Squared Error, RMSE
Rsquared = 1.0 - (numpy.var(absError) / numpy.var(yData))

print()
print('RMSE:', RMSE)
print('R-squared:', Rsquared)

print()