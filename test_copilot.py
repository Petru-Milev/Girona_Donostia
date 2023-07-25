import numpy as np

def calculate_distance_between_two_points(point1, point2):
    """Calculate the distance between two points in 3D space.
    
    Parameters
    ----------
    point1 : list
        List of three floats representing the coordinates of the first point.
    point2 : list
        List of three floats representing the coordinates of the second point.
        
    Returns
    -------
    distance : float
        Distance between the two points.
    """
    distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    return distance
