import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 

#!!!
#Path to the file from where we read the data 
#Modify this to change your file 

path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/m062x_c_ultrafine.csv"


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
dr = "Fourth"
nr_poin = str(5)
what = "Energy"
column = 83
dx = "Z"
dy = "d^4 Energy/dZ^4"

###!!! Change here for the title of the plots
fig.suptitle(dr + " Derivative of "+what+" m062x_c_ultrafine," + nr_poin + " points", fontsize = 40)

for i, ax in enumerate(axes_flattened):
    #!!! Change here for column of the data. np.float64(matrix[:,3]) is by default. Change the 3 to the desired column to use it as x axis
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
#!!! Change here for the name of the file
plt.savefig("subplot_" + dr + "_deriv_" + what + "_" + nr_poin +  "_points_m062x_ultrafine.png")