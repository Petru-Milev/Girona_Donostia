from functions_for_library import *
from romberg import *
from objects_for_library import Gaussian_File
from objects_for_library import Fchk_File
import numpy as np
from itertools import product
import ast
import matplotlib.pyplot as plt
import copy
import matplotlib.ticker as ticker 

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/input_test_2_august/lib_bnnt-3_M062X.txt"
#read_input_file(path)

path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example5_Romberg/Example5_Romberg.txt"
read_calc_deriv_file(path)

#read_input_file(path)