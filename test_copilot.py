import numpy as np

def taylor_series(x, n):
    """
    This function calculates the Taylor series of a function f(x) = exp(x) around x = 0.
    :param x: the point around which the Taylor series is calculated
    :param n: the number of terms in the Taylor series
    :return: the value of the Taylor series at x
    """
    return np.sum([x**i/np.math.factorial(i) for i in range(n)])
