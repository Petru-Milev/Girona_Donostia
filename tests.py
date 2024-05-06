import numpy as np 
from functions_for_library import read_field_and_energy_from_orca_file, read_folder_with_orca_files
from romberg import romberg_procedure
from functions_for_library import make_profiles_romberg_procedure

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/andrei_code/integrals/LiH_integrals/LiH_wb97xd_6-31+G(d)_integrals.csv"

matrix = np.loadtxt(path, delimiter=",", skiprows=1)
#v_x = np.float128(matrix[:,0])
#v_y = np.float128(matrix[:,1])
v_x = np.array([x for x in range(300)])
v_y = np.array([x**3 for x in v_x])
A =  make_profiles_romberg_procedure(v_x, v_y, order = 2, a = 2, min_size_matrix= 2, nr_elements= 7, spacing = 1)
print(A)

np.savetxt("test.csv", A, delimiter = ",", fmt='%.6f')

