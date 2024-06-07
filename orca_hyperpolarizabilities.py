import numpy as np 
import os
from romberg import romberg_procedure
#from romberg import romberg_procedure


def create_inputs(path_input, path_output=None, derivative_type='romberg', romberg_points = 6 ):

    if path_output is None:
        path_output = os.getcwd()              #It will save the files in the folder where script is being run

    with open(path_input, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if ('!' not in line) and ('efield' in line):
            efield_line = i
            break
    
    file_name = os.path.basename(path_input) #Get the name of the file
    file_name = file_name.split('.')[0]  #Remove the extension
    name_original = file_name + '_origin.inp'
    with open(os.path.join(path_output, name_original), 'w') as f:
        f.writelines(lines)
        
    if derivative_type.lower() == 'romberg':
        exponents = np.arange(1, romberg_points+1)
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
    else: 
        print('Derivative type not recognized. Please use romberg')
    return 

def extract_polarizability_tensor(path_file):
    alpha_tensor, diagonalized_tensor, P = None, None, None
    with open(path_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'THE POLARIZABILITY TENSOR' in line:                         #Looking for this line in outfile
            polarizability_tensor_lines = lines[i:i+15]                 #Extracting the lines with the polarizability tensor
            break
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
        
def extract_data_from_folder(path_folder):
    

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

    dir = {'x': 0, 'y': 1, 'z': 2}
    header = 'x,y,z,alpha_xx,alpha_xy,alpha_xz,alpha_yx,alpha_yy,alpha_yz,alpha_zx,alpha_zy,alpha_zz'
    data = np.zeros((1,12))
    files = os.listdir(path_folder)
    for file in files:
        if not file.endswith('.out'):
            continue
        if ('efield' not in file) and ('_origin' in file):
            print(file)
            alpha_tensor, diagonalized_tensor, P = extract_polarizability_tensor(os.path.join(path_folder, file))
            alpha_tensor = alpha_tensor.flatten()
            line = np.concatenate((np.zeros(3), alpha_tensor))
            data = np.vstack((data, line))
            continue
        path_file = os.path.join(path_folder, file)
        field_str = file.split('_efield_')[1].split('.out')[0] #Eliminating the beging of the file, and the extension
        field_str = field_str.split('_') #spliting the y_-0.0004 into y and -0.0004
        field = np.zeros(3)             #Field 0 0 0 
        field[dir[field_str[0]]] = np.longdouble(field_str[1]) #Field 0 -0.0004 0
        alpha_tensor, diagonalized_tensor, P = extract_polarizability_tensor(path_file)
        alpha_tensor = alpha_tensor.flatten()
        line = np.concatenate((field, alpha_tensor))
        data = np.vstack((data, line))
    data = data[1:]
    data[:, :3] = np.round(data[:, :3], 4)
    data = data[data[:, 0].argsort()]
    data = sort_data(data)
    np.savetxt(os.path.join(path_folder, 'polarizabilities.csv'), data, delimiter=',', header=header)
    return data

def calc_beta_from_alpha(data):
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

    beta = np.array([beta_xxx, beta_xyy, beta_xzz, beta_yxx, beta_yyy, beta_yzz, beta_zxx, beta_zyy, beta_zzz, beta_xyz])
    return beta

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







def get_beta_quantities(beta_vector):
    def get_beta_3d(beta_vector):
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
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (1/35)*sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (2/105)*sum(beta_3d[i,i,i] * beta_3d[i, j, j] for i in indices for j in indices if i != j)
        term3 = (11/105)*sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (1/105)*sum(beta_3d[i, j, j] * beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != j)
        term5 = (1/105)* sum(beta_3d[i,j,k]**2 for i in indices for j in indices for k in indices if i != j and i != k and j != k)
        result = term1 - term2 + term3 - term4 + term5
        return result
    
    def DR(avg_beta_zzz_sqr, avg_beta_zxx_sqr):
        return avg_beta_zzz_sqr / avg_beta_zxx_sqr
    
    def beta_hrs(avg_beta_zzz_sqr, avg_beta_zxx_sqr):
        DR = avg_beta_zzz_sqr / avg_beta_zxx_sqr
        beta_hrs = np.sqrt(avg_beta_zzz_sqr * (1 + 1/DR))
        return beta_hrs
    
    def beta_j_one(beta_3d):
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (2/5) * sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (6/5) * sum(beta_3d[i, i, i] * beta_3d[i,j,j] for i in indices for j in indices if i != j)
        term3 = (3/5) * sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (3/5) * sum(beta_3d[i, j, j]*beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k )

        result = term1 + term2 + term3 + term4
        return result
    
    def beta_j_three(beta_3d):
        if beta_3d.shape != (3,3,3):
            raise ValueError('Beta tensor must be 3x3x3')
        
        indices = range(3)

        term1 = (2/5) * sum(beta_3d[i,i,i]**2 for i in indices)
        term2 = (6/5) * sum(beta_3d[i, i, i] * beta_3d[i,j,j] for i in indices for j in indices if i != j)
        term3 = (12/5) * sum(beta_3d[i, j, j]**2 for i in indices for j in indices if i != j)
        term4 = (3/5) * sum(beta_3d[i, j, j]*beta_3d[i, k, k] for i in indices for j in indices for k in indices if i != j and i != k and j != k )
        term5 = (1/4) * sum(beta_3d[i, j, k]**2 for i in indices for j in indices for k in indices if i != j and i != k and j != k)

        result = term1 - term2 + term3 - term4 + term5 
        return result   
    
    def anisotropy_parameter(beta_j_three, beta_j_one):
        return beta_j_three/beta_j_one
    
    beta_3d = get_beta_3d(beta_vector)
    print(f"Shape of beta3d is {beta_3d.shape}")
    var_avg_beta_zzz_sqr = avg_beta_zzz_sqr(beta_3d)
    var_avg_beta_zxx_sqr = avg_beta_zxx_sqr(beta_3d)
    var_DR = DR(var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr)
    var_beta_hrs = beta_hrs(var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr)
    var_beta_j_one = beta_j_one(beta_3d)
    var_beta_j_three = beta_j_three(beta_3d)
    var_anisotropy_parameter = anisotropy_parameter(var_beta_j_three, var_beta_j_one)

    lst = [var_avg_beta_zzz_sqr, var_avg_beta_zxx_sqr, var_DR, var_beta_hrs, var_beta_j_one, var_beta_j_three, var_anisotropy_parameter]
    
    return lst



if __name__ == '__main__':
    path = "/Users/petrumilev/Library/CloudStorage/GoogleDrive-petia.md36@gmail.com/Other computers/Do_not_delete_from_here/a.me/Master CNE/Study Materials/Master_Thesis/Ruben_Derivatives/Geom1_LiH.inp"
    #folder_output = "/Users/petrumilev/Desktop/orca_outputs"
    #path_output = "/Users/petrumilev/Library/CloudStorage/GoogleDrive-petia.md36@gmail.com/Other computers/Do_not_delete_from_here/a.me/Master CNE/Study Materials/Master_Thesis/Ruben_Derivatives/E_Y/a1_Y_-0.0004.out"
    folder_output = "/Users/petrumilev/Desktop/LiH_wb97xd"
    #create_inputs(path, derivative_type='romberg', romberg_points = 6)
    #alpha_tensor, diagonalized_tensor, P = extract_polarizability_tensor(path_output)
    #A = extract_data_from_folder(folder_output)
    #beta = calc_beta_from_alpha(A)
    print('x,y,z,xxx,xyy,xzz,yxx,yyy,yzz,zxx,zyy,zzz,xyz')
    #print(beta)
    print('--------------')
    #lst =get_beta_quantities(beta)
    file_gaussian = "/Users/petrumilev/Library/CloudStorage/GoogleDrive-petia.md36@gmail.com/Other computers/Do_not_delete_from_here/a.me/Master CNE/Study Materials/Master_Thesis/Ruben_Derivatives/bmimcl.log"

    beta = extract_beta_from_gaussian_output(file_gaussian)
    print(beta)
    for i in beta:
        print(i)
    
