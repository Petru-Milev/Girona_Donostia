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

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/fes_fchk"

#A = get_list_of_propreties_for_fchk_in_a_folder(path, ["Z", "XZ"])
#A = print_derivatives(A[1])
#np.savetxt("new_file.csv", A[1], delimiter=",", fmt='%s', header=",".join(str(v) for v in A[0]))

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/input_test_2_august/M062X_101.txt"
read_input_file(path)