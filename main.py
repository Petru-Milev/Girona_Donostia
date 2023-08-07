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
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/m062x_c_ultrafine_from_dipole_moment.csv"
with open(path, "r") as file:
    lines = file.readlines()
names = lines[0].strip().split(",")
matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype = str)

fig, axes = plt.subplots(3, 5, figsize=(50, 30))

axes_flattened = axes.flatten()

fig.suptitle("Second Derivative of Dipole M062X_c_ultrafine, 5 points", fontsize = 40)

for i, ax in enumerate(axes_flattened):
    ax.plot(np.float64(matrix[:,3]), np.float64(matrix[:, 53 + i]),  ".", label = "step = " + str(i+1), markersize = 12)
    ax.set_title("Step = " + str(i+1), fontsize = 20)
    ax.set_xlabel("Z", fontsize = 16)
    ax.set_ylabel("d^2E/dZ^2", fontsize = 16)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.legend(fontsize = 24)
    """ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.001))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.0005))"""
    ax.tick_params(axis='x', labelsize=16) 
    ax.tick_params(axis='y', labelsize=16) 
    x_formatter = ticker.FormatStrFormatter('%.4f')
    y_formatter = ticker.FormatStrFormatter('%.2f')
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    #ax.grid(which="both", axis="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.savefig("subplot_second_deriv_dipole_5_points.png")


#np.savetxt("data_from_folder_ultrafine_deriv_two_from_dipole.csv", A[1], fmt="%s", delimiter=",", header=",".join([name for name in A[0]]))


#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/input_test_2_august/lib_bnnt-3_M062X.txt"
#read_input_file(path)