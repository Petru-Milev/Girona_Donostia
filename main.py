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

#path = '/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/28th July/Test_input/Input_kw_example.txt'
#read_input_for_electric_field_from_file_and_generate_files(path, extension=".txt")

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/28th July/Test_input"
#update_oldchk_for_files_in_a_folder(path, file_extension=".txt")

#kw = ["IOp(3/14=-6)", "word4", "word5", "GFOutput"]
#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Input_kw_example_Y+0_Z+0.txt"
#add_keywords(path, *kw)

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/fes_fchk_ultrafine"
#A = get_list_of_propreties_for_fchk_in_a_folder(path, ["Z"])
#np.savetxt("data_from_folder_ultrafine.csv", A[1], fmt="%s", delimiter=",", header=",".join([name for name in A[0]]))

#fig, ax = plt.subplots(figsize=(40, 24))


#for i in range(0, 14):
    #A = print_derivatives(A[0], A[1], 3, 5, order = 2, n_points = 3, step = i+1)
    #ax.plot(np.float128(np.array((A[1]))[:,3]), np.float128(np.array((A[1]))[:, -1]), "o", label = "step = " + str(i+1), markersize = 15)
#ax.set_title("sec Derivative of dipole with Respect to Field" + str(i+1))
#ax.set_xlabel("Z")
#ax.set_ylabel("d dipole /dZ")
#ax.get_xaxis().get_major_formatter().set_useOffset(False)
#ax.get_yaxis().get_major_formatter().set_useOffset(False)
#ax.legend(fontsize = 24)
#ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
#ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
#ax.yaxis.set_major_locator(ticker.MultipleLocator(0.001))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.0005))
#ax.grid(which="both", axis="both", linestyle="--", linewidth=0.5)
#plt.savefig("overlay_deriv_two_dipole.png")
#np.savetxt("data_from_folder_ultrafine_deriv_two_from_dipole.csv", A[1], fmt="%s", delimiter=",", header=",".join([name for name in A[0]]))


path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/test_methods_2_aug/wB97X/wB97X/lib_bnnt-3_wB97X.txt"
read_input_file(path)

