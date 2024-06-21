import numpy as np 
import os
from girona_donostia.romberg import romberg_procedure
from girona_donostia.functions_for_library import calc_first_derivative
#from romberg import romberg_procedure
#from romberg import romberg_procedure


def create_inputs(path_input, path_output=None, derivative_type='romberg', points = 6, h = 0.0005):
    """    This function will create a series of input files with different electric fields
    The input file is an orca input file
    This input file will be used as a template to generate a series of input files with different electric fields
    """
    if path_output is None:
        path_output = os.getcwd()              #It will save the files in the folder where script is being run

    with open(path_input, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        #Looking for the line with the electric field
        if ('!' not in line) and ('efield' in line):
            efield_line = i
            break
    
    file_name = os.path.basename(path_input) #Get the name of the file
    file_name = file_name.split('.')[0]  #Remove the extension
    name_original = file_name + '_origin.inp'
    with open(os.path.join(path_output, name_original), 'w') as f:
        f.writelines(lines)
        
    if derivative_type.lower() == 'romberg':
        #Creating a series for romberg derivatives
        exponents = np.arange(1, points+1)
        powers_of_2 = np.power(2, exponents)*10**(-3)  #To be used to generate romberg exponents
        powers_of_2 = np.concatenate((-powers_of_2[::-1], powers_of_2)) #Add negative values
        directions = [0, 1, 2] #x, y, z
        directions_dict = {0: 'x', 1: 'y', 2: 'z'}
        for direction in directions:
            for power in powers_of_2:
                line = np.zeros(3)
                line[direction] = power
                line = [str(x) for x in line]
                line = ' efield ' + ' , '.join(line) + '\n'
                lines[efield_line] = line
                name_to_save = file_name + '_efield_' + directions_dict[direction] + '_' + str(power) + '.inp'
                with open(os.path.join(path_output, name_to_save), 'w') as f:
                    f.writelines(lines)
    elif (derivative_type.lower() == 'central_diff') or (derivative_type.lower() == 'central_difference') or (derivative_type.lower() == 'central differences') or (derivative_type.lower() == 'central dif'):
        #Creating a series for central differences
        directions = [0, 1, 2]
        directions_dict = {0: 'x', 1: 'y', 2: 'z'}
        amplitude = h*(points//2)
        space = np.linspace(-amplitude, amplitude, points)
        for direction in directions:
            for point in space:
                if point == 0:
                    continue
                line = np.zeros(3)
                line[direction] = point
                line = [str(x) for x in line]
                line = ' efield ' + ' , '.join(line) + '\n'
                lines[efield_line] = line
                name_to_save = file_name + '_efield_' + directions_dict[direction] + '_' + str(point) + '.inp'
                with open(os.path.join(path_output, name_to_save), 'w') as f:
                    f.writelines(lines)
    else: 
        print('Derivative type not recognized. Please use romberg')
    return 

def extract_polarizability_tensor(path_file):
    alpha_tensor, diagonalized_tensor, P = None, None, None
    with open(path_file, 'r') as f:
        lines = f.readlines()

    index = -1 
    for i, line in enumerate(lines):
        if 'THE POLARIZABILITY TENSOR' in line:                         #Looking for this line in outfile
            #index = len(lines) - 1 
            #polarizability_tensor_lines = lines[index:index+15]                 #Extracting the lines with the polarizability tensor
            index = i
    if index != -1:
        polarizability_tensor_lines = lines[index:index+15]
    else:
        print('Polarizability tensor not found in the file')
        return alpha_tensor, diagonalized_tensor, P
    for i, line in enumerate(polarizability_tensor_lines):                 
        if 'the raw cartesian tensor (atomic units):' in line.lower():
            row_1 = polarizability_tensor_lines[i+1]
            row_2 = polarizability_tensor_lines[i+2]
            row_3 = polarizability_tensor_lines[i+3]
            row_1 = [np.longdouble(x) for x in row_1.split()]
            row_2 = [np.longdouble(x) for x in row_2.split()]
            row_3 = [np.longdouble(x) for x in row_3.split()]
            alpha_tensor = np.array([row_1, row_2, row_3])  #Returning raw cartesian polarisability tensor
            break
    for i, line in enumerate(polarizability_tensor_lines):
        if 'diagonalized tensor' in line.lower():
            diagonalized_tensor = polarizability_tensor_lines[i+1]
            diagonalized_tensor = np.array([np.longdouble(x) for x in diagonalized_tensor.split()])
            break
    for i, line in enumerate(polarizability_tensor_lines):
        if 'diagonalized tensor' in line.lower():
            raw_1 = polarizability_tensor_lines[i+3]
            raw_2 = polarizability_tensor_lines[i+4]
            raw_3 = polarizability_tensor_lines[i+5]
            raw_1 = [np.longdouble(x) for x in raw_1.split()]
            raw_2 = [np.longdouble(x) for x in raw_2.split()]
            raw_3 = [np.longdouble(x) for x in raw_3.split()]
            P = np.array([raw_1, raw_2, raw_3])
            break
    return alpha_tensor, diagonalized_tensor, P
        
def extract_data_from_folder(path_folder, save_data = True):

    def extract_field(file):
        field = np.zeros(3)
        with open(file, 'r') as f:
            lines = f.readlines()   
        for line in lines:
            if ('efield' in line) and ('NAME' not in line):
                line = line.split("efield")
                line = line[1].split(",")
                for i, item in enumerate(line):
                    line[i] = item.strip()
                field = np.array([np.longdouble(x) for x in line])
                break
        else:
            return None
        return field

    def sort_data(data): 
        data_x = data[data[:, 0] != 0]
        data_y = data[data[:, 1] != 0]
        data_z = data[data[:, 2] != 0]
        data_x = data_x[data_x[:, 0].argsort()]
        data_y = data_y[data_y[:, 1].argsort()]
        data_z = data_z[data_z[:, 2].argsort()]
        data_origin = data[np.isclose(data[:, :3], 0).all(axis=1)]
        data = np.vstack((data_origin, data_x, data_y, data_z))
        return data

    dir = {'x': 0, 'y': 1, 'z': 2, 'X':0, 'Y':1, 'Z':2}
    header = 'x,y,z,alpha_xx,alpha_xy,alpha_xz,alpha_yx,alpha_yy,alpha_yz,alpha_zx,alpha_zy,alpha_zz'
    data = np.zeros((1,12))
    files = os.listdir(path_folder)
    for file in files:
        if not file.endswith('.out'):
            continue
        path_file = os.path.join(path_folder, file)
        field = extract_field(path_file)
        if field is None:
            continue
        alpha_tensor, diagonalized_tensor, P = extract_polarizability_tensor(path_file)
        alpha_tensor = alpha_tensor.flatten()
        line = np.concatenate((field, alpha_tensor))
        data = np.vstack((data, line))
    data = data[1:]
    data[:, :3] = np.round(data[:, :3], 4)
    data = data[data[:, 0].argsort()]
    data = sort_data(data)
    if save_data:
        np.savetxt(os.path.join(path_folder, 'polarizabilities.csv'), data, delimiter=',', header=header)
    return data

def calc_beta_from_alpha(data, derivative_type='romberg'):
    #Data header 
    #x,y,z,alpha_xx,alpha_xy,alpha_xz,alpha_yx,alpha_yy,alpha_yz,alpha_zx,alpha_zy,alpha_zz

    origin_line = data[0,:]
    data = data[1:]
    data_x = data[data[:, 0] != 0]
    index_x = data_x.shape[0]//2
    data_x = np.insert(data_x, index_x, origin_line, axis=0)
    data_y = data[data[:, 1] != 0]
    index_y = data_y.shape[0]//2
    data_y = np.insert(data_y, index_y, origin_line, axis=0)
    data_z = data[data[:, 2] != 0]
    index_z = data_z.shape[0]//2
    data_z = np.insert(data_z, index_z, origin_line, axis=0)

    #print(data_z[:, 2])
    
    if derivative_type.lower() == 'romberg':
        beta_xxx = romberg_procedure(data_x[:, 0], data_x[:, 3])
        beta_xyy = romberg_procedure(data_y[:, 1], data_y[:, 4])
        beta_xzz = romberg_procedure(data_z[:, 2], data_z[:, 5])
        beta_yxx = romberg_procedure(data_x[:, 0], data_x[:, 6])
        beta_yyy = romberg_procedure(data_y[:, 1], data_y[:, 7])
        beta_yzz = romberg_procedure(data_z[:, 2], data_z[:, 8])
        beta_zxx = romberg_procedure(data_x[:, 0], data_x[:, 9])
        beta_zyy = romberg_procedure(data_y[:, 1], data_y[:, 10])
        beta_zzz = romberg_procedure(data_z[:, 2], data_z[:, 11])
        beta_xyz = romberg_procedure(data_z[:, 2], data_z[:, 4])

        beta = -1*np.array([beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz])
        return beta
    elif (derivative_type.lower() == 'central_diff') or (derivative_type.lower() == 'central_difference') or (derivative_type.lower() == 'central differences') or (derivative_type.lower() == 'central dif'):
        n_points = data_x.shape[0]
        list_points_for_first_derivative = [3, 5, 7, 9, 11]
        if n_points not in list_points_for_first_derivative:
            raise ValueError('Number of points for first derivative must be 3, 5, 7, 9, 11')
        beta_xxx = calc_first_derivative(data_x[:, 0], data_x[:, 3], n_points = n_points, step = 1)
        beta_xyy = calc_first_derivative(data_y[:, 1], data_y[:, 4], n_points = n_points, step = 1)
        beta_xzz = calc_first_derivative(data_z[:, 2], data_z[:, 5], n_points = n_points, step = 1)
        beta_yxx = calc_first_derivative(data_x[:, 0], data_x[:, 6], n_points = n_points, step = 1)
        beta_yyy = calc_first_derivative(data_y[:, 1], data_y[:, 7], n_points = n_points, step = 1)
        beta_yzz = calc_first_derivative(data_z[:, 2], data_z[:, 8], n_points = n_points, step = 1)
        beta_zxx = calc_first_derivative(data_x[:, 0], data_x[:, 9], n_points = n_points, step = 1)
        beta_zyy = calc_first_derivative(data_y[:, 1], data_y[:, 10], n_points = n_points, step = 1)
        beta_zzz = calc_first_derivative(data_z[:, 2], data_z[:, 11], n_points = n_points, step = 1)
        beta_xyz = calc_first_derivative(data_z[:, 2], data_z[:, 4], n_points = n_points, step = 1)
        beta = -1*np.array([beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz])
        return beta
    else:
        print('Derivative type not recognized. Please use romberg or central_diff')
        return None

def extract_beta_from_gaussian_output(path_file):
    """
    Extracting beta values from gaussian log file 
    Extracting  Beta (dipole orientation)  Beta(0;0,0):
    output is in the following format 
    return np.array([beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz])
    """
    beta = None
    with open(path_file, 'r') as f:
        lines = f.readlines()
    

    for i, line in enumerate(lines):
        if ('Beta(0;0,0)' in line) and ('(dipole orientation)' in lines[i-4]):
            lines = lines[i+8:i+18]
            break
    else:
        print('Beta not found in the file')
        return beta
    
    dict_beta_comp = {}
    #Not iterating through beta values 
    for i, line in enumerate(lines):
        line = line.split()
        dir = line[0]
        val = float(line[1].replace('D', 'e')) #replacing 0.137447D+03
        dict_beta_comp[dir] = val
    beta = np.array([dict_beta_comp['xxx'], dict_beta_comp['yxy'], dict_beta_comp['zxz'], dict_beta_comp['xxy'], dict_beta_comp['yyy'], dict_beta_comp['zyz'], dict_beta_comp['xxz'], dict_beta_comp['yyz'], dict_beta_comp['zzz'], dict_beta_comp['yxz']])
    return beta

def get_beta_quantities_from_beta_vector(beta_vector):
    #beta_vector = np.array([beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz])
    #returns [var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr, var_DR, var_beta_hrs, var_beta_j_one, var_beta_j_three, var_anisotropy_parameter]
    #Paper https://doi.org/10.1021/jp107165k

    def get_beta_3d(beta_vector):
        #Input Beta is static first hyperpolarizability
        #By using symmetry opperation construct all 27 elements of the beta vector 
        beta_xyz = beta_vector[-1]
        beta = beta_vector[:-1]
        beta = beta.reshape((3,3))
        """beta = 
        [[beta_xxx, beta_xyy, beta_xzz],
        [beta_yxx, beta_yyy, beta_yzz],
        [beta_zxx, beta_zyy, beta_zzz]]"""
        beta_3d = np.zeros((3,3,3))
        beta_3d[:,:,:] = None
        beta_3d[0,0,0] = beta[0,0]
        beta_3d[0,1,1] = beta[0,1]
        beta_3d[0,2,2] = beta[0,2]
        beta_3d[1,0,0] = beta[1,0]
        beta_3d[1,1,1] = beta[1,1]
        beta_3d[1,2,2] = beta[1,2]
        beta_3d[2,0,0] = beta[2,0]
        beta_3d[2,1,1] = beta[2,1]
        beta_3d[2,2,2] = beta[2,2]
        beta_3d[0,1,2] = beta_xyz
        
        has_NaN = True
        while has_NaN:
            has_NaN = np.any(np.isnan(beta_3d))
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        if np.isnan(beta_3d[i,j,k]):
                            beta_3d[i,j,k] = beta_3d[i,k,j]
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        if np.isnan(beta_3d[i,j,k]):
                            beta_3d[i,j,k] = beta_3d[k,j,i]
        return beta_3d
    
    def avg_beta_zzz_sqr(beta_3d):
        #Formula 3a in the paper
        
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (1/7) * sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (6/35) * sum(beta_3d[i, i, i] * beta_3d[i,j,j] for i in indices for j in indices if i != j)
        term3 = (9/35) * sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (9/105) * sum(beta_3d[i, j, j]*beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k )
        term5 = (1/70) * sum(beta_3d[i, j, k]**2 for i in indices for j in indices for k in indices if i != j and i != k and j != k)

        result = term1 + term2 + term3 + term4 + term5
        return result

    def avg_beta_zxx_sqr(beta_3d):
        #Formula 3b in the paper
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (1/35)*sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (2/105)*sum(beta_3d[i,i,i] * beta_3d[i, j, j] for i in indices for j in indices if i != j)
        term3 = (11/105)*sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (1/105)*sum(beta_3d[i, j, j] * beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k)
        term5 = (1/105)* sum(beta_3d[i,j,k]**2 for i in indices for j in indices for k in indices if i != j and i != k and j != k)
        result = term1 - term2 + term3 - term4 + term5
        return result
    
    def DR(avg_beta_zzz_sqr, avg_beta_zxx_sqr):
        #Formula 4 in the paper
        return avg_beta_zzz_sqr / avg_beta_zxx_sqr
    
    def beta_hrs(avg_beta_zzz_sqr, avg_beta_zxx_sqr):
        #Formula 5 in the paper
        DR = avg_beta_zzz_sqr / avg_beta_zxx_sqr
        beta_hrs = np.sqrt(avg_beta_zzz_sqr * (1 + 1/DR))
        return beta_hrs
    
    def beta_j_one(beta_3d):
        #Formula 9a in the paper
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (3  /5) * sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (6/5) * sum(beta_3d[i, i, i] * beta_3d[i,j,j] for i in indices for j in indices if i != j)
        term3 = (3/5) * sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (3/5) * sum(beta_3d[i, j, j]*beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k )

        result = np.sqrt(term1 + term2 + term3 + term4)
        return result
    
    def beta_j_three(beta_3d):
        #Formula 9b in the paper
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (2/5) * sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (6/5) * sum(beta_3d[i, i, i] * beta_3d[i,j,j] for i in indices for j in indices if i != j)
        term3 = (12/5) * sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (3/5) * sum(beta_3d[i, j, j]*beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k )
        term5 = (1/4) * sum(beta_3d[i, j, k]**2 for i in indices for j in indices for k in indices if i != j and i != k and j != k)

        result = np.sqrt(term1 - term2 + term3 - term4 + term5)
        return result   
    
    def anisotropy_parameter(beta_j_three, beta_j_one):
        #Small formula right below the formula (6) in the paper
        return beta_j_three/beta_j_one
    
    beta_3d = get_beta_3d(beta_vector)
    #print(f"Shape of beta3d is {beta_3d.shape}")
    var_avg_beta_zzz_sqr = avg_beta_zzz_sqr(beta_3d)
    var_avg_beta_zxx_sqr = avg_beta_zxx_sqr(beta_3d)
    var_DR = DR(var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr)
    var_beta_hrs = beta_hrs(var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr)
    var_beta_j_one = beta_j_one(beta_3d)
    var_beta_j_three = beta_j_three(beta_3d)
    var_anisotropy_parameter = anisotropy_parameter(var_beta_j_three, var_beta_j_one)

    lst = [var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr, var_DR, var_beta_hrs, var_beta_j_one, var_beta_j_three, var_anisotropy_parameter]
    
    return lst

def get_beta_quantities_from_alpha_orca(path_folder, path_to_save, derivative_type='romberg'):
    data = extract_data_from_folder(path_folder, save_data = False)
    beta = calc_beta_from_alpha(data, derivative_type=derivative_type)
    lst = get_beta_quantities_from_beta_vector(beta)
    alpha = data[0, 3:]
    alpha = alpha.reshape((3,3))
    beta_to_print = "beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz"
    beta_to_print = beta_to_print.split(", ")
 
    with open(path_to_save, 'w') as f:
        f.write('Numerical Calculation of Beta quantities from Alpha tensor obtained in Orca\n')
        f.write(f"Definition of quantities: https://doi.org/10.1021/jp107165k\n")
        f.write("-----------------------------------------------------------------------------\n")
        f.write("Alpha tensor:\n")
        f.write(f"alpha(0,0), w=static:\n")
        f.write(f"{alpha}\n\n")
        f.write("Beta tensor:\n")
        f.write(f"beta(0,0,0), w=static:\n")
        for i, item in enumerate(beta_to_print):
            f.write(f"{item}: {beta[i]}\n")
        f.write('\n')
        f.write("Beta_quantities:\n")
        A = "[var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr, var_DR, var_beta_hrs, var_beta_j_one, var_beta_j_three, var_anisotropy_parameter]"
        A = "<B2zzz>, <B2xx>, DR, beta_hrs, B|J=1|, B|J=3|, anisotropy_parameter"
        A = A.split(", ")
        for i, item in enumerate(A):
            f.write(f"{item}: {np.round(lst[i], 6)}\n")

def get_beta_quantities_from_beta_gaussian(path_to_file, path_to_save, derivative_type = 'romberg'):
    beta = extract_beta_from_gaussian_output(path_to_file)
    lst = get_beta_quantities_from_beta_vector(beta)
    beta_to_print = "beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz"
    beta_to_print = beta_to_print.split(", ")
    with open(path_to_save, 'w') as f:
        f.write('Numerical Calculation of Beta quantities from Beta tensor obtained in Gaussian (input orientation)\n')
        f.write(f"Definition of quantities: https://doi.org/10.1021/jp107165k\n")
        f.write("-----------------------------------------------------------------------------\n")
        f.write("Beta tensor:\n")
        f.write(f"beta(0,0,0), w=static:\n")
        for i, item in enumerate(beta_to_print):
            f.write(f"{item}: {beta[i]}\n")
        f.write('\n')
        f.write("Beta_quantities:\n")
        A = "[var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr, var_DR, var_beta_hrs, var_beta_j_one, var_beta_j_three, var_anisotropy_parameter]"
        A = "<B2zzz>, <B2xx>, DR, beta_hrs, B|J=1|, B|J=3|, anisotropy_parameter"
        A = A.split(", ")
        for i, item in enumerate(A):
            f.write(f"{item}: {np.round(lst[i], 6)}\n")



if __name__ == '__main__':
    print("Hola mundo!")
