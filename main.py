from functions_for_library import *
from romberg import *
from objects_for_library import Gaussian_File
from objects_for_library import Fchk_File
import numpy as np
from itertools import product
import ast
import matplotlib.pyplot as plts
import copy
import matplotlib.ticker as ticker 

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/input_test_2_august/lib_bnnt-3_M062X.txt"
#read_input_file(path)

#path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example6_Curve_Fit/Example6.txt"

#path_b3lyp = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/meetings/25th_August/Curve_Fit/stats_b3lyp.txt"
#path_wB97x = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/meetings/25th_August/Curve_Fit/stats_wB97X.txt"
#path_m062x = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/meetings/25th_August/Curve_Fit/stats_m062x.txt"
#path_lc_blyp = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/meetings/25th_August/Curve_Fit/stats_lc_blyp.txt"


#read_calc_deriv_file(path_b3lyp)
#read_calc_deriv_file(path_wB97x)
#read_calc_deriv_file(path_m062x)
#read_calc_deriv_file(path_lc_blyp)

#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/meetings/25th_August/CD_Derivatives/stats_m062x.txt"
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Romberg_25th_Aug/lc_blyp_ultrafine/lib_bnnt-3_LC-BLYP.txt"
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Romberg_25th_Aug/lc_blyp_ultrafine/lib_bnnt-3_LC-BLYP.txt"
read_input_file(path)

print("hello world")
