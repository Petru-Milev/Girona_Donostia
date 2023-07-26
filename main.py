from functions_for_library import *
from objects_for_library import Gaussian_File
import numpy as np
from itertools import product
import ast

#start()
#update_oldchk_for_files_in_a_folder("/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia", ".inp", "n_minus_one")

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Input_kw_example.txt"
#read_input_for_electric_field_from_file_and_generate_files(path, extension=".txt")

kw = ["IOp(3/14=-6)", "word4", "word5", "GFOutput"]
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Input_kw_example_Y+0_Z+0.txt"
add_keywords(path, *kw)