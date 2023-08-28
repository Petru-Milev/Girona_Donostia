import numpy as np 

def mae(actatual_vector, forecast_vector):
    result_vector = np.abs(actatual_vector - forecast_vector)
    result = np.nanmean(result_vector)
    return result
def mape(actual_vector, forecast_vector):
    result_vector = np.abs((actual_vector - forecast_vector))/actual_vector
    result = np.nanmean(result_vector) * 100
    return result

def rmse(actual_vector, forecast_vector):
    result_vector = (actual_vector - forecast_vector)**2
    result = np.sqrt(np.nanmean(result_vector))
    return result

def max(actual_vector, forecast_vector):
    result_vector = np.abs(actual_vector - forecast_vector)
    result = np.nanmax(result_vector)
    return result

def maxre(actual_vector, forecast_vector):
    result_vector = np.abs(actual_vector - forecast_vector)/actual_vector
    result = np.nanmax(result_vector) * 100
    return result

