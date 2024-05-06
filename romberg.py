import numpy as np 


def romberg_procedure(vector_x, vector_y, order = 1, a = 2, min_size_matrix = 2, return_only_value = True):
    """
    Function to Generate the Romberg Matrix
    h - the smallest step size
    a - coefficient for the Generalized Romberg Procedure
    k - is related to the distance from of the initial points from x = 0
    min_size_matrix - the minimum size of the matrix for looking for stability region in the Resulting Romberg Matrix
    RR1, RR2, RR3, RR4 - are the relations for the first, second, third and fourth derivatives for Romberg procedure
    PP1, PP2, PP3, PP4 - iterative formulas to improve the generalized romberg procedure
    Data submitted to this function is in the form of vectors, which start from the most negative value, go to zero, and then
    go to the most positive value. The vectors are of the same size.
    This function also returns the stability region for the Romber Matrix. 
    It stores in four dimensional tensors all maximum and minimum values of all the possible submatrices of the Romberg Matrix.
    For example, Min[row, column, sub_row, sub_column] - row and column are the starting possition of the submatrix
    The sub_row and sub_column are the length and width of the submatrix. Min stores the minimal values, max stores the max values in this submatrix. 
    Then we do the difference of Max and Min matrix, and we look for the smallest element of it. 
    The indexes of the smallest element will tell us the position of the stability region.  
    """
    def RR1(fp1, fm1, h, a, k):
        return (fp1 - fm1)/(2*(a**k) *h)
    def RR2(f0, fp1, fm1, h, a, k): 
        return (fm1 + fp1 - 2 * f0)/(((a**k)*h)**2)
    def RR3(fp1, fm1, fp2, fm2, h, a, k):
        return 3*(-fm2 + a*fm1 - a*fp1 + fp2)/(a*(a**2 -1)*((a**k)*h)**3)
    def RR4(f0, fp1, fm1, fp2, fm2, h, a, k):
        first_term = 12*(fm2 - (a**2)*fm1 + 2*(a**2-1)*f0)/((a**2)*(a**2 - 1)*((a**k) * h)**4)
        second_term = 12*(-(a**2)*fp1 + fp2)/((a**2) * (a**2 - 1) * ((a**k) * h)**4)
        return first_term + second_term
    order = str(order)
    
    zero_index = int((len(vector_x) - 1)/2)  #Vector_x or vector_y will always has an odd number of elements
    h = abs(vector_x[zero_index] - vector_x[zero_index + 1]) 
    if order == "1" or order == "2":
        p_max = int((len(vector_x)-1)/2) - 1
    if order == "3" or order == "4":
        p_max = int((len(vector_x)-1)/2) - 2

    romberg_matrix = np.full((p_max+1, p_max+1), np.NaN, dtype=np.longdouble) #Creating an empry matrix with NaN values
    def P1(p, k):
        if p == 0:
            romberg_matrix[k, p] = RR1(vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], h, a, k)
            return RR1(vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], h, a, k)
        else:
            romberg_matrix[k, p] = (a**(2*p) * P1(p-1, k) - P1(p-1, k+1))/(a**(2*p) -1) 
            return (a**(2*p) * P1(p-1, k) - P1(p-1, k+1))/(a**(2*p) -1)
    def P2(p, k):
        if p == 0:
            romberg_matrix[k, p] = RR2(vector_y[zero_index], vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], h, a, k)
            return RR2(vector_y[zero_index], vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], h, a, k)
        else:
            romberg_matrix[k, p] = (a**(2*p) * P2(p-1, k) - P2(p-1, k+1))/(a**(2*p) -1) 
            return (a**(2*p) * P2(p-1, k) - P2(p-1, k+1))/(a**(2*p) -1)
    def P3(p, k):
        if p == 0:
            romberg_matrix[k, p] = RR3(vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], vector_y[zero_index + k + 2], vector_y[zero_index - k - 2], h, a, k)
            return RR3(vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], vector_y[zero_index + k + 2], vector_y[zero_index - k - 2], h, a, k)
        else:
            romberg_matrix[k, p] = (a**(2*p) * P3(p-1, k) - P3(p-1, k+1))/(a**(2*p) -1) 
            return (a**(2*p) * P3(p-1, k) - P3(p-1, k+1))/(a**(2*p) -1)
    def P4(p, k):
        if p == 0:
            romberg_matrix[k, p] = RR4(vector_y[zero_index], vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], vector_y[zero_index + k + 2], vector_y[zero_index - k - 2], h, a, k)
            return RR4(vector_y[zero_index], vector_y[zero_index + k + 1], vector_y[zero_index - k - 1], vector_y[zero_index + k + 2], vector_y[zero_index - k - 2], h, a, k)
        else:
            romberg_matrix[k, p] = (a**(2*p) * P4(p-1, k) - P4(p-1, k+1))/(a**(2*p) -1) 
            return (a**(2*p) * P4(p-1, k) - P4(p-1, k+1))/(a**(2*p) -1)
    
    map_P = {"1": P1, "2": P2, "3": P3, "4": P4}
    map_P[order](p_max, 0)                  #Getting Romberg Matrix
    np.savetxt("romberg_matrix.csv", romberg_matrix, delimiter = ",")
    #plt.imshow(romberg_matrix, cmap='hot', interpolation='nearest')
    #plt.colorbar()
    #plt.savefig("romberg_matrix_heatmap.png")
    """
    Evaluating Romberg Triangle
    """

    rows, columns, sub_rows, sub_columns = romberg_matrix.shape[0], romberg_matrix.shape[1], romberg_matrix.shape[0], romberg_matrix.shape[1] 

    matrix_min = np.full((rows, columns, sub_rows, sub_columns), np.NaN, dtype=np.longdouble)
    matrix_max = np.full((rows, columns, sub_rows, sub_columns), np.NaN, dtype=np.longdouble)
    
    for row in range(rows):
        for column in range(columns):
            sub_rows = rows - (row + 1)
            sub_columns = columns - (column + 1)
            for sub_row in range(min_size_matrix, sub_rows):
                for sub_column in range(min_size_matrix, sub_columns):
                    matrix = romberg_matrix[row:row+sub_row, column:column+sub_column]
                    nan_mask = np.isnan(matrix)
                    contains_nan = np.any(nan_mask)
                    if contains_nan:
                        continue
                    else:
                        #print(f"row: {row}, column: {column}, sub_row: {sub_row}, sub_column: {sub_column}")
                        #print(romberg_matrix[row:row+sub_row + 2, column:column+sub_column + 2])
                        matrix_min[row, column, sub_row, sub_column] = np.nanmin(romberg_matrix[row:row+sub_row, column:column+sub_column])
                        matrix_max[row, column, sub_row, sub_column] = np.nanmax(romberg_matrix[row:row+sub_row, column:column+sub_column])
    resulting_matrix = np.longdouble(matrix_max) - np.longdouble(matrix_min)
    min_value = np.nanmin(resulting_matrix) 
    for i1 in range(resulting_matrix.shape[0]):
        for i2 in range(resulting_matrix.shape[1]):
            for i3 in range(resulting_matrix.shape[2]):
                for i4 in range(resulting_matrix.shape[3]):
                    if resulting_matrix[i1, i2, i3, i4] == min_value:
                        min_element_index = (i1, i2, i3, i4)
                        #print(f"Minimum element is row: {i1}, column: {i2}, sub_row: {i3}, sub_column: {i4}")
                        #print(f"Maximum element is {matrix_max[i1, i2, i3, i4]}")
                        #print(f"Minimum element is {matrix_min[i1, i2, i3, i4]}")
                        #print(f"Difference of elements of element is {resulting_matrix[i1, i2, i3, i4]}")
                        #print(romberg_matrix[i1:i1+i3, i2:i2+i4])
                        value_to_return = np.average(romberg_matrix[i1:i1+i3, i2:i2+i4])
                        break
    #value_to_return = 0 
    if return_only_value:
        return value_to_return
    else:
        return [romberg_matrix, min_element_index, resulting_matrix]

if __name__ == "__main__":
    #v_x = [-0.01619826068, -0.0115701862, -0.00826441871, -0.00590315622, -0.00421654016, -0.0030118144, -0.002151296, -0.00153664, -0.0010976, -0.000784, -0.00056, -0.0004, 0, 0.0004, 0.00056, 0.000784, 0.0010976, 0.00153664, 0.002151296, 0.0030118144, 0.00421654016, 0.00590315622, 0.00826441871, 0.0115701862, 0.01619826068]
    v_x = [-0.0256, -0.0128, -0.0064, -0.0032, -0.0016, -0.0008, -0.0004, 0, 0.0004, 0.0008, 0.0016, 0.0032, 0.0064, 0.0128, 0.0256]
    #print(len(v_x))
    #v_x = [-0.4096 ,-0.2048, -0.1024, -0.0512, -0.0256, -0.0128, -0.0064, -0.0032, 0, 0.0032, 0.0064, 0.0128, 0.0256, 0.0512, 0.1024, 0.2048, 0.4096]
    v_x = np.float64(np.array(v_x))
    a = 2.0
    a = np.float64(a)
    #v_y = -a/np.tan(v_x + 0.04)
    #v_y = np.sin(2*(v_x - 3)) * np.exp(-1/10 * (v_x-3)**2)
    #print(v_y)
    #v_x = np.array([-0.08, -0.04, -0.02, -0.01, -0.005, 0, 0.005, 0.01, 0.02, 0.04, 0.08])
    #v_y = np.array([-76.3618181251, -76.3653502973, -76.3663297729, -76.3665877636, -76.3666539614, 0,  -76.3666533658, -76.3665834835, -76.3662964810, -76.3650852057, -76.3596812418])
    v_x = np.array([-16, -8, -4, -2, -1, 0, 1, 2, 4, 8, 16]) + 10
    v_y = v_x**2 + 10 
    A = romberg_procedure(v_x, v_y, order = 1, a = 2, min_size_matrix= 2, return_only_value = False)
    print(A[0])
    A = np.vstack((v_x, v_y)).T
    #print(A)
    np.savetxt("data_for_romberg.csv", A, delimiter = ",", fmt='%s')
