import numpy as np

import numpy as np
def find_submatrix_with_min_difference(arr):    
    if arr.size == 0:
        return None
    min_diff = float('inf')    
    best_submatrix = None
    # Iterate over all possible top-left and bottom-right corners of submatrices
    for i in range(arr.shape[0]):        
        for j in range(arr.shape[1]):
            for k in range(i, arr.shape[0]):                
                for l in range(j, arr.shape[1]):
                    submatrix = arr[i:k+1, j:l+1]                    
                    diff = submatrix.max() - submatrix.min()
                    if diff < min_diff:                       
                        min_diff = diff
                        best_submatrix = submatrix
    return best_submatrix
# Test
arr = np.array([[10, 3.5, 5.1], [2.1, 6.1, 4.1], [7.1, 8.1, 9.1], [2.1, 3.1, 5.1], [2.1, 6.1, 4.1], [7.1, 8.1, 9.1], [1.1, 3.1, 5.1], [2.1, 6.1, 4.1], [7.1, 8.1, -1.1]])
print(find_submatrix_with_min_difference(arr))