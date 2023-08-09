from functions_for_library import *
from objects_for_library import Gaussian_File
from objects_for_library import Fchk_File
import numpy as np
from itertools import product
import ast
import matplotlib.pyplot as plt
import copy
import matplotlib.ticker as ticker 

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/wB97X_c_ultrafine.csv"

with open(path, "r") as file:
    lines = file.readlines()
names = lines[0].strip().split(",")
matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype = str)

fig, axes = plt.subplots(3, 5, figsize=(50, 30))

axes_flattened = axes.flatten()

dr = "Fourth"
nr_poin = str(5)
what = "Energy"
column = 83
dx = "Z"
dy = "d^4Energy/dZ^4"

fig.suptitle(dr + " Derivative of "+what+" wB97X_c_ultrafine," + nr_poin + " points", fontsize = 40)

for i, ax in enumerate(axes_flattened):
    ax.plot(np.float64(matrix[:,3]), np.float64(matrix[:, column + i]),  ".", label = "step = " + str(i+1), markersize = 12)
    ax.set_title("Step = " + str(i+1), fontsize = 20)
    ax.set_xlabel(dx, fontsize = 16)
    ax.set_ylabel(dy, fontsize = 16)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.legend(fontsize = 24)
    ax.tick_params(axis='x', labelsize=16) 
    ax.tick_params(axis='y', labelsize=16) 
    x_formatter = ticker.FormatStrFormatter('%.4f')
    y_formatter = ticker.FormatStrFormatter('%.2f')
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)

plt.tight_layout()
plt.savefig("subplot_" + dr + "_deriv_" + what + "_" + nr_poin +  "_points_wB97X_ultrafine.png")