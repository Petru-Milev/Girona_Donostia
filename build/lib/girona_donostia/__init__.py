import numpy as np
from scipy.optimize import curve_fit
from itertools import product
import ast
import os
import copy 
import datetime as dt

#from girona_donostia import functions_for_library
#from girona_donostia import  objects_for_library
from girona_donostia.objects_for_library import *
from girona_donostia.functions_for_library import *
from girona_donostia.romberg import *
from girona_donostia.statistic import * 
from girona_donostia.curve_fit import *
from girona_donostia.hyperpolarizabilities import *

__version__ = "0.1.14"
__author__ = "Petru Milev"

print(f"Link to Wiki Page is: {'https://github.com/Petru-Milev/Girona_Donostia/wiki'}")
print(f"Version of the package is: {__version__}")

