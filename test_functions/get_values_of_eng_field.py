import numpy as np
import os
import copy
def extract_data_from_fchk_file_for_numerical_derivation(file_path):
    """
    This function extracts "Total Energy", "Dipole Moment", "Polarizability", "HyperPolarizability", "Quadrupole Moment" from a function. 
    The result is an object of Fchk_File instance, containing all the important values
    Input is the absolute path to the file. 
    """
    obj = Fchk_File(name = file_path.split("/")[-1])                        #Creating instance of an object
    def save_lines_after_keyword(input_file, keyword):                      #Getting the numerical values after the specified keywords
        with open(input_file, "r") as file:                                 #Keywords are Dipole Moment, Hyperpolarizability etc
            no_keyword_in_file = True
            for line_number, line in enumerate(file, start = 1):            #Lopping over all the file and searching for line with the keyword
                if keyword in line:                                     
                    imp_line = (line_number, line)                          #Saving number of the line and the line itself
                    no_keyword_in_file = False
                    break
        if no_keyword_in_file:                                              #If the keyword has not been found in the file, return a False value
            return False
        words = imp_line[1].split()                                        
        for i in range(len(words)):                                         #Looking for the number of values of the vector. 
            if words[i] == "N=":                                            #In the saved line it is after the word N= 
                n = int(words[i+1])                                         #Saving number of values that vector has
        start_line = imp_line[0] + 1                                        #Getting start and end of the line we need to save
        finish_line = imp_line[0] + np.ceil(n/5)

        lines_to_save = [] 
        with open(input_file, "r") as file:                                 #Saving the lines with the values in a list, later to be transfered into and np.array
            current_line = 1                                                
            for line in file:                                               #Looping over all lines
                if start_line <= current_line <= finish_line:               #Finding starting and finishing line
                    lines_to_save.append(line.strip())                      #Saving the lines with the numerical values
                current_line += 1 
        lines_to_save = [np.float128(item) for sublist in lines_to_save for item in sublist.split()]            #Saving the number saved as str into float values with 128 bytes
        return lines_to_save
    
    def get_electric_field_values_and_eng_value(input_file):                              #A fundtion to get value of electric field, as the previous function does not allow for this.
        with open(input_file, "r") as file:                                 #Oppening the file
            line_n_minus1 = ""
            for line_number, line in enumerate(file, start = 1):            #Looping over lines of the file
                if "External E-field" in line_n_minus1:                     #if in the previous line was the keyword
                    imp_line = (line_number, line.split())                  #than save the line (which is after the keyword and which contains the values for the electric field)
                elif "Total Energy" in line:
                    energy = np.float128(line.strip().split()[3])
                line_n_minus1 = line
    

        e_field_1 = imp_line[1][1:4]                                        #Values of the electric field are saved in position 1, 2, 3 of the resulting vector 
        e_field_1 = [np.float128(x) for x in e_field_1]                     #Converting str to an appropriate numerical value
        return (e_field_1, energy)                                                    

    e_field_and_eng_value = get_electric_field_values_and_eng_value(file_path)

    list_kw = ["Dipole Moment", "Polarizability", "HyperPolarizability", "Quadrupole Moment"]
    resulting_dict = {}
    for i in list_kw:                                                       #Getting actual values
        resulting_dict[i] = save_lines_after_keyword(file_path, i)
    obj.e_field = e_field_and_eng_value[0]                                  #Assigning this values to an instance of Fchk_File object
    obj.energy = e_field_and_eng_value[1]
    obj.dipole_moment = resulting_dict["Dipole Moment"]
    obj.polarizability = resulting_dict["Polarizability"]
    obj.hyperpolarizability = resulting_dict["HyperPolarizability"]
    obj.quadrupole_moment = resulting_dict["Quadrupole Moment"]
    return obj                                                              #Returning the object

class Fchk_File():
    """
    This class is used to store the data from a fchk file.
    """
    def __init__(self, name = False, e_field = False, energy = False, dipole_moment = False, polarizability = False, hyperpolarizability = False, quadrupole_moment = False):
        self.name = name
        self.e_field = e_field
        self.energy = energy
        self.dipole_moment = dipole_moment
        self.polarizability = polarizability
        self.hyperpolarizability = hyperpolarizability
        self.quadrupole_moment = quadrupole_moment
    
    def list_propreties(self, directions):
        """
        This function returns a list of propreties of the object if they are present.
        The input is a list of directions for which to return the propreties.
        """
        map_directions_1 = {"x" : 0, "y" : 1, "z" : 2, "xx" : 0, "yy" : 2, "zz" : 5, "xxx" : 0, "yyy" : 3, "zzz" : 9}
        map_dipole = {"x" : 0, "y" : 1, "z" : 2}
        map_polarizability = {"xx" : 0, "xy" : 1, "yy" : 2, "xz" : 3, "yz" : 4, "zz" : 5}
        map_hyperpolarizability = {"xxx" : 0, "xxy" : 1, "xyy" : 2, "yyy" : 3, "xxz" : 4, "xyz" : 5, "yyz" : 6, "xzz" : 7, "yzz" : 8, "zzz" : 9}
        main_directions = []      #if direction x, y or z is specified, it will be saved here, later to print also the xx, yy, zz, xxx, yyy, zzz
        secondary_directions = []   #All other directions which will be printed only once
        for char in directions:     #Separating the directions in the input file
            if char.lower() in map_dipole:
                main_directions.append(char)
            else: secondary_directions.append(char)

        new_list = [["Name", "E_Field_X", "E_Field_Y", "E_Field_Z", "Energy", "Dipole_Moment", "Polarizability", "Hyperpolarizability"]]
        new_list.append([])         #Creating the list in the form [[*names], [*values]
        new_list[1].append(self.name)
        new_list[1].extend(self.e_field)
        new_list[1].append(self.energy)
        if self.dipole_moment:          
            count = 0
            position = new_list[0].index("Dipole_Moment")
            del new_list[0][position]
            for i in main_directions:                   #Printing it for all the specified main directions
                new_list[0].insert(position + count, "Dipole_Moment_" + i.lower())
                new_list[1].append(self.dipole_moment[map_directions_1[i.lower()]])
                count += 1
        else: 
            del new_list[0][position]
            print("Dipole_Moment is not present in the file")

        if self.polarizability:
            count = 0
            position = new_list[0].index("Polarizability")
            del new_list[0][position]
            for i in main_directions:                  #Printing it for all the specified main directions       
                new_list[0].insert(position + count, "Polarizability_" + 2*i.lower())
                new_list[1].append(self.polarizability[map_directions_1[2*i.lower()]])
                count += 1
            if secondary_directions:                #Printing it for all the specified secondary directions
                for i in secondary_directions:
                    if i.lower() in map_polarizability:
                        new_list[0].insert(position + count, "Polarizability_" + i.lower())
                        new_list[1].append(self.polarizability[map_polarizability[i.lower()]])
                        count += 1
        else: 
            del new_list[0][position]
            print("Polarizability is not present in the file")
        
        if self.hyperpolarizability:
            count = 0
            position = new_list[0].index("Hyperpolarizability")
            del new_list[0][position]
            for i in main_directions:
                new_list[0].insert(position + count, "Hyperpolarizability_" + 3*i.lower())
                new_list[1].append(self.hyperpolarizability[map_directions_1[3*i.lower()]])
                count += 1
            if secondary_directions:
                for i in secondary_directions:
                    if i.lower() in map_hyperpolarizability:
                        new_list[0].insert(position + count, "Hyperpolarizability_" + i.lower())
                        new_list[1].append(self.hyperpolarizability[map_hyperpolarizability[i.lower()]])
                        count += 1

        else: 
            del new_list[0][position]
            print("Hyperpolarizability is not present in the file")
        return new_list

def get_list_of_propreties_for_fchk_in_a_folder(folder_path, directions, sort_values_direction = False, return_list_of_objects = False):
    """
    This function returns a list of propreties of the object if they are present.
    The input is a list of directions for which to return the propreties.
    folder_path is the path to the folder with the fchk files
    directions is a list of directions for which to return the propreties
    sort_values_direction is the direction according to which to sort the files
    return_list_of_objects is a boolean value, if True, the function returns a list of objects containing propreties of the file, if False, it returns a list of propreties
    """
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".fchk")]                #Getting list of files in the folder. 
    map_directiosn_1 = {"x" : 0, "y" : 1, "z" : 2}                                                                                              #Mapping the direction to the corresponding integer                                                                                  #Getting the index for the corresponding direction
    map_direction_int_to_char = {"0" : "x", "1" : "y", "2" : "z"}
    list_with_data_from_files = []                                                                                                              #List to save de data 

    for i in files:                                                                                                                             #Extracting the data from files in an instance of an object.
        obj = extract_data_from_fchk_file_for_numerical_derivation(os.path.join(folder_path, i))
        list_with_data_from_files.append(copy.deepcopy(obj))                                                                                    #Saving it to a list later to work

    
    
    if sort_values_direction:
        direction_int = map_directiosn_1[sort_values_direction.lower()]                                                                         #Getting the index for the corresponding direction
    else: 
        for i in list_with_data_from_files[0].e_field:
            if i != 0:
                direction_int = list_with_data_from_files[0].e_field.index(i)
                print("E_field according to which to sort the files is not specified and the first non-zero value of the electric field is taken as a direction to sort the files")
                print("The sorting directin is: " + map_direction_int_to_char[str(direction_int)].upper())
                break

    list_with_data_from_files = sorted(list_with_data_from_files, key = lambda elem: elem.e_field[direction_int])                                #Sorting the data according to the values of electric field. 
    
    if return_list_of_objects:                                                                                                                   #If the user wants to get the list of objects, return it
        return list_with_data_from_files
    
    names = list_with_data_from_files[0].list_propreties(directions)[0]                                                                          #Getting names for the atributes of the attribute of the object
    list_with_data_from_files = [obj.list_propreties(directions)[1] for obj in list_with_data_from_files]                                        #Getting the list of propreties 
    
    return [names, list_with_data_from_files]



def calc_first_derivative(vector_x, f, n_points = 3, step = 1):
    """
    This function calculates the first derivative of a function f(x)
    :param vector_x: the vector of x values
    :param f: the vector of f(x) values
    :param n_points: the number of points to use for the derivative
    :param step: the step size
    :return: the vector of f'(x) values
    !!!If new function is added, it should be checked that no boundary conditions are violated!!!
    """
    def three_points(i, step, h):
        return (-1*f[i - step]+1*f[i + step])/(2*1.0*(h*step)**1)
    def five_points(i, step, h):
        return (1*f[i-2*step]-8*f[i-1*step]+0*f[i+0]+8*f[i+1*step]-1*f[i+2*step])/(12*1.0*(h*step)**1)
    def ten_points():
        return 10
    i = 0
    map_functions = {"3" : three_points, "5" : five_points}
    f_x = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_x(i, step, h))
    return derivative_vector

def calc_second_derivative(vector_x, f, n_points = 3, step = 1):
    """
    This function calculates the second derivative of a function f(x)
    :param vector_x: the vector of x values
    :param f: the vector of f(x) values
    :param n_points: the number of points to use for the derivative
    :param step: the step size
    :return: the vector of f''(x) values
    !!!If new function is added, it should be checked that no boundary conditions are violated!!!
    """
    def three_points(i, step, h):
        return (1*f[i-step]-2*f[i+0]+1*f[i+step])/(1*1.0*(h*step)**2)
    def five_points(i, step, h):
        return (-1*f[i-2*step]+16*f[i-step]-30*f[i+0]+16*f[i+step]-1*f[i+2*step])/(12*1.0*(h*step)**2)
    map_functions = {"3" : three_points, "5" : five_points}
    f_xx = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_xx(i, step, h))
    return derivative_vector

def calc_third_derivative(vector_x, f, n_points = 5, step = 1):
    """
    This function calculates the third derivative of a function f(x)
    :param vector_x: the vector of x values
    :param f: the vector of f(x) values
    :param n_points: the number of points to use for the derivative
    :param step: the step size
    :return: the vector of f'''(x) values
    !!!If new function is added, it should be checked that no boundary conditions are violated!!!
    """
    def five_points(i, step, h):
        return (-1*f[i-2]+2*f[i-1]+0*f[i+0]-2*f[i+1]+1*f[i+2])/(2*1.0*(h*step)**3)
    map_functions = {"5" : five_points}
    f_xxx = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_xxx(i, step, h))
    return derivative_vector


def print_derivatives(names, list_propreties, derivative_x_vector_index, derivative_y_vector_index, order = 1, n_points = 3, step = 1):
    
    """
    This function prints the derivatives of a function f(x) = y
    :param names: the list of names of the propreties
    :param list_propreties: the list of propreties
    :param derivative_x_vector_index: the index of the x vector in the list of propreties
    :param derivative_y_vector_index: the index of the y vector in the list of propreties
    :param order: the order of the derivative
    :param n_points: the number of points to use for the derivative
    :param step: the step size
    :return: the list of names and the list of propreties with the derivatives
    """
    
    map_derivative = {"1" : calc_first_derivative, "2": calc_second_derivative, "3" : calc_third_derivative}
    derivative = map_derivative[str(order)]
 
    #Printing energy derivatives
    if not isinstance(list_propreties, np.ndarray):
        list_propreties = np.array((list_propreties))     

    arr = derivative(np.float128(list_propreties[:, derivative_x_vector_index]), np.float128(list_propreties[:, derivative_y_vector_index]), n_points=n_points, step=step)

    while (len(list_propreties[:,derivative_y_vector_index]) - len(arr)) % 2 == 0 and (len(list_propreties[:,derivative_y_vector_index]) - len(arr)) > 0:
        arr = np.insert(arr, 0, np.NaN)
        arr = np.append(arr, np.NaN)
    names.append("Derivative_order_" + str(order) + "_number_points_" + str(n_points) + "_" +str(names[derivative_y_vector_index]) + "_div_" + str(names[derivative_x_vector_index]))
    list_propreties = np.vstack((list_propreties.T, arr)).T
    return [names, list_propreties]

#names, list_propreties, index_energy, order = 1, n_points = 3, step = 1
A = get_list_of_propreties_for_fchk_in_a_folder("/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/fes_fchk", ["X", "Y", "Z", "XZ", "YYZ"])
A = print_derivatives(names = A[0], list_propreties = A[1], derivative_x_vector_index= 3, derivative_y_vector_index= 4, order = 1, n_points = 3, step = 1)
A = print_derivatives(names = A[0], list_propreties = A[1], derivative_x_vector_index= 3, derivative_y_vector_index= 4, order = 2, n_points = 3, step = 1)
A = print_derivatives(names = A[0], list_propreties = A[1], derivative_x_vector_index= 3, derivative_y_vector_index= 4, order = 3, n_points = 5, step = 1)

np.savetxt("data.csv", A[1], delimiter=",", fmt='%s', header=",".join(str(v) for v in A[0]))
np.savetxt("data.tab", A[1], delimiter="\t", fmt='%s', header=",".join(str(v) for v in A[0]))