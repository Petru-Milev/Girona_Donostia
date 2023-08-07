import numpy as np
from itertools import product
import ast
from objects_for_library import Gaussian_File
import os
from objects_for_library import Fchk_File
import copy
from itertools import product
from functions_for_library import *
import datetime as dt

def read_calc_deriv_file(path_to_file):
    """
    This function reads the input file and calculates the derivatives for the specified columns
    Input is path to the input file. 
    Output is a csv file with the data and all calculated derivatives
    Also, it will save the initial data without calculated derivatives
    """
    path_to_folder = "/".join(path_to_file.split("/")[:-1])     #Getting the path to the folder
    original_file_name = path_to_file.split("/")[-1]            #Getting the name of the file
    log_file = path_to_file[:-4] + "_WARNINGS_log.txt"          #Creating the log file

    with open(log_file, "w") as log_file:                       #Creating the log file
        log_file.write("Log file for " + original_file_name + "\n")
    
    file_input = None
    with open(path_to_file, "r") as file:                       #Reading the input file lines
        file_input = file.readlines()
    
    keywords = []           
    for line in file_input:                                     #Getting the keywords from the input file
        if line.strip() == "":
            break
        else: keywords.append(line.strip())
    
    temp = []
    for line in keywords:                                       #Getting the keywords as a list of strings
        temp.extend(split_text_for_inp(line))
    keywords = copy.deepcopy(temp[1:])

    input_for_function = []
    for i, word in enumerate(keywords):                         #Separating the keywords, into the keywords and the options for them
        input_for_function.append(get_inp_text(word))
        keywords[i] = word.split("(")[0]
    print("Keywords and input for function")
    print(keywords)
    print(input_for_function)
    print("-------------------------------------")
    if ("read_data" in keywords) or ("extract_from_folder" in keywords):        #Finding the path from which we will read file or a folder
        for line in file_input:
            if "@" in line:
                path_to_read = line.strip()[1:]
                break
    
    if "read_data" in keywords:                                                 #This will read a .csv or .txt file
        index = keywords.index("read_data")
        options = input_for_function[index]
        options = options[0].split(", ")
        delimiter = ","
        skiprows = 0 
        if options != None and any("delimiter" in i for i in options):          #Delimiter is the separator between the columns
            print("here delimiter")
            for i in options:
                if delimiter in i:
                    delimiter = i.split("=")[1]
                    delimiter = delimiter[1:-1]
                    break
        if options != None and any("header" in i for i in options):             #Specifying if our file has a header
            skiprows = 1
            with open(path_to_read, "r") as file:                                
                for line in file:
                    names = line.strip().split(delimiter)
                    break
        else:                                                                   #Case when rows are not present, to create the names of the columns
            with open(path_to_read, "r") as file:
                for line in file:
                    names = line.strip().split(delimiter)
                    for i, name in enumerate(names):
                        names[i] = "Column_" + str(i)
                    break
        
        if "skiprows" in options:                                               #Skipping firsnt n rows from the file
            for i in options:
                if skiprows in i:
                    print(line)
                    skiprows = int(i.split("=")[1])
                    break
        matrix = np.loadtxt(path_to_read, delimiter=delimiter, skiprows=skiprows, dtype=str)

    if "extract_from_folder" in keywords:                                       #Extracting data from fchk files in a folder and saving it in a .csv file
        index = keywords.index("extract_from_folder")
        options = input_for_function[index]
        directions = ["X", "Y", "Z"]                                            #Unless specified otherwise, we will extract the data for all directions
        if options[0] != None:                                                  #If options were specified 
            options = split_text_for_inp(options[0])                            #Splitting the options
            if any("directions" in i for i in options):                         #Seeing if we have specified directions
                for i in options:                                               #Getting the directions
                    if "directions" in i:
                        directions = i.split("=")[1]                            #Spliting the directions=(X, Y, Z) string
                        directions = directions[1:-1]                           #Removing the brackets
                        directions = directions.split(",")                      #Spliting the directions
                        break
        matrix = get_list_of_propreties_for_fchk_in_a_folder(path_to_read, directions=directions)
        names = matrix[0]
        matrix = np.array(matrix[1])
        np.savetxt("data_from_folder.csv", matrix, fmt="%s", delimiter=",", header=",".join([name for name in names]))

    if "var" in keywords:                                                       #Specifiying a variable to iterate over
        index = keywords.index("var")       
        options = input_for_function[index]
        options = split_text_for_inp(options[0])                                #Variables are of the format var(name=(start,finish,step)=type)     
        list_of_variables = {}                                                  #We will save here the list of variables
        for i in options:
            if i.split("=")[2] == "int":
                list_of_variables[i.split("=")[0]] = [int(x) for x in i.split("=")[1][1:-1].split(",")]
            if i.split("=")[2] == "float":
                list_of_variables[i.split("=")[0]] = [float(x) for x in i.split("=")[1][1:-1].split(",")]
            else: list_of_variables[i.split("=")[0]] = [int(x) for x in i.split("=")[1][1:-1].split(",")]
    print("List of variables")
    print(list_of_variables)

    for i, line in enumerate(file_input):
        data = {"order":1, "up": 5, "down": 4, "points": 3, "step": 1}          #Creating the data dictionary with default values
        if "derivative" in line.lower().strip() and "@" not in line.strip().lower() and "path_to_save" not in line.strip().lower():                                #Looking for the derivative line
            keys = line.strip().split(",")                                      #The line looks like this Derivative(Order=1,up=4,down=3,points=3,step=x)
            keys[-1] = keys[-1][:-1]                                            #Removing the ) from the last key
            keys[0] = keys[0][11:]                                              #Removing the derivative from the first key and the (
            for key in keys:
                data[key.split("=")[0].strip().lower()] = key.split("=")[1].strip().lower()  #Introducing the data in the dictionary
            for key, value in data.items():                                     #Converting the values to the correct type
                if value in list_of_variables:                                  #If variable is present in the list of variables, we will iterate over it
                    range_of_values = np.arange(*list_of_variables[value])      #Creating the list with values
                    data[key] = range_of_values                                 #Changing the value of the key to the list of values
                else:
                    data[key] = int(value)                            
            data_copied = copy.deepcopy(data)                                   #Will be used for looping over the variables
            if any(isinstance(value, np.ndarray) for value in data.values()):   #Checking if there are variables to iterate over
                for key, value in data.items():
                    if isinstance(value, np.ndarray):
                        for i in value:                                         #Iterating over the variables 
                            data_copied[key] = i                                
                            names, matrix = print_derivatives(names, matrix, derivative_x_vector_index= data_copied["down"], derivative_y_vector_index = data_copied["up"], order = data_copied["order"], n_points = data_copied["points"], step = data_copied["step"])
            else: names, matrix = print_derivatives(names, matrix, derivative_x_vector_index= data_copied["down"], derivative_y_vector_index = data_copied["up"], order = data_copied["order"], n_points = data_copied["points"], step = data_copied["step"])
    
    current_time = dt.datetime.now()                                            #To be used to save the data if the name to save is not specified
    path_to_save = "data_" + str(current_time.hour) + "h_" + str(current_time.minute) + "min.csv"
    for line in file_input:                                                     #Looking for path to save
        if "path_to_save" in line:                                            
            path_to_save = line.strip().split("=")[1]
            break
    np.savetxt(path_to_save, matrix, fmt="%s", delimiter=",", header=",".join([name for name in names]))    #Saving the data

path = "/Users/petrumilev/Documents/projects_python/project_girona_donostia/Examples/Derivatives/Example1.txt"
read_calc_deriv_file(path)