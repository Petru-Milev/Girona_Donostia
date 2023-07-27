from functions_for_library import *
from objects_for_library import Gaussian_File
from objects_for_library import Fchk_File
import numpy as np
from itertools import product
import ast
import matplotlib.pyplot as plt
import copy
import matplotlib.ticker as ticker 

#start()
#update_oldchk_for_files_in_a_folder("/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia", ".inp", "n_minus_one")

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Input_kw_example.txt"
#read_input_for_electric_field_from_file_and_generate_files(path, extension=".txt")

#kw = ["IOp(3/14=-6)", "word4", "word5", "GFOutput"]
#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Input_kw_example_Y+0_Z+0.txt"
#add_keywords(path, *kw)

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/fes_fchk"

A = get_list_of_propreties_for_fchk_in_a_folder(path, ["Z"])

for i in range(10):
    A = print_derivatives(A[0], A[1], derivative_x_vector_index=3, derivative_y_vector_index=4,order = 2, n_points=3, step = i+1)

fig, axs = plt.subplots(2, 5, figsize = (24, 12))
ind = 12
B = copy.deepcopy(A)
for i, ax in enumerate(axs.flatten()):
    B = print_derivatives(B[0], B[1], derivative_x_vector_index=3, derivative_y_vector_index=12, order = 1, n_points=3, step = i+1)
    ind += 1
    #plt.scatter(np.float128(A[1][:, 3]), np.float128(A[1][:,-1]))
    #plt.title('Plot for step = ' + str(i+1))
    #plt.close()
    ax.scatter(np.float128(B[1][:, 3]), -1 * np.float128(B[1][:,-1]))
    ax.set_title('first d of second d, step is ' + str(i+1))
    ax.set_xlabel('Z_field')
    ax.set_ylabel("Deriv Value")
#plt.tight_layout()
#plt.savefig('OVerlay.png')
plt.savefig("parallel_plot_sec_deriv_derivated.png")
np.savetxt("data_second_derivative_derivated.csv", B[1], delimiter=",", fmt='%s', header=",".join(str(v) for v in B[0]))