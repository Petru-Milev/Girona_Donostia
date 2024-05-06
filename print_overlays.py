import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 

#!!!
#Path to the file from where we read the data 
#Modify this to change your file 

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/HF/data_500_points/data_HF_500_points_conver_9.csv"

#path_conver11 = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/derivatives/data_5k_points/wb97x/numerical_derivatives_nb_wb97x.csv"
with open(path, "r") as file:
    lines = file.readlines()
names = lines[0].strip().split(",")
matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype = str)

fig, axes = plt.subplots(3, 5, figsize=(50, 30))

axes_flattened = axes.flatten()


"""
Change here for the names in the folders 
dr - derivative
nr_poin - number of points
what - what we are taking the derivative of
column - column of the data
dx - x axis name
dy - y axis name
"""
dr = "Third"
nr_poin = str(5)
what = "Energy"
column = 8
dx = "Z"
dy = "d^3E/dz^3"
a = 0

###!!! Change here for the title of the plots
fig.suptitle(dr + " Derivative of "+what+" HF_conver_9, " + nr_poin + " derivative_points", fontsize = 40)

for i, ax in enumerate(axes_flattened): 
    #!!! Change here for column of the data. np.float64(matrix[:,3]) is by default. Change the 3 to the desired column to use it as x axis
    ax.plot(np.float64(matrix[:,3]), np.float64(matrix[:, 7]),marker ="o", label = "analytical")
    ax.plot(np.float64(matrix[:,3]), -1*np.float64(matrix[:, column + i]),  ".", label = "h = " + str("{:.2e}".format(abs(np.float64(matrix[(i+a)*1+1,3]) - np.float64(matrix[0,3])))), markersize = 12)

    ax.set_title("Step = " + str((i+a)*1+1), fontsize = 20)
    ax.set_xlabel(dx, fontsize = 16)
    ax.set_ylabel(dy, fontsize = 16)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.legend(fontsize = 24)
    ax.tick_params(axis='x', labelsize=16) 
    ax.tick_params(axis='y', labelsize=16) 
    ax.set_ylim(1300, 5500)
    x_formatter = ticker.FormatStrFormatter('%.4f')
    y_formatter = ticker.FormatStrFormatter('%.2f')
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)

plt.tight_layout()
#!!! Change here for the name of the file
#plt.savefig(f"Overlay_subplot_{dr}_deriv_{what}_{nr_poin}_points_m062x_ultrafine_5k_big_steps_25.png")
plt.savefig("HF_conver_9.png")
