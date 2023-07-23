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
    def __init__(self, name = False, e_field = False, energy = False, dipole_moment = False, polarizability = False, hyperpolarizability = False, quadrupole_moment = False):
        self.name = name
        self.e_field = e_field
        self.energy = energy
        self.dipole_moment = dipole_moment
        self.polarizability = polarizability
        self.hyperpolarizability = hyperpolarizability
        self.quadrupole_moment = quadrupole_moment
    
    def list_propreties(self, direction):
        map_directions = {"x" : 0, "y" : 1, "z" : 2, "xx" : 0, "yy" : 2, "zz" : 5, "xxx" : 0, "yyy" : 3, "zzz" : 9}
        new_list = [["Name", "Electric_Field_Direction_" + direction, "Energy", "Dipole_Moment", "Polarizability", "Hyperpolarizability"]]
        new_list.append([])
        new_list[1].append(self.name)
        new_list[1].append(self.e_field[map_directions[direction.lower()]])
        new_list[1].append(self.energy)
        if self.dipole_moment:
            new_list[1].append(self.dipole_moment[map_directions[direction.lower()]])
        else: new_list[1].append("Not_present")
        if self.polarizability:
            new_list[1].append(self.polarizability[map_directions[2*direction.lower()]])
        else: new_list[1].append("Not_present")
        if self.hyperpolarizability:
            new_list[1].append(self.hyperpolarizability[map_directions[3*direction.lower()]])
        else: new_list[1].append("Not_present")
        return new_list

def get_list_of_propreties_for_fchk_in_a_folder(folder_path, direction):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".fchk")]                #Getting list of files in the folder. 
    map_directiosn_1 = {"x" : 0, "y" : 1, "z" : 2}                                                                                              #Mapping the direction to the corresponding integer 
    direction_int = map_directiosn_1[direction.lower()]                                                                                         #Getting the index for the corresponding direction
    list_with_data_from_files = []                                                                                                              #List to save de data 

    for i in files:                                                                                                                             #Extracting the data from files in an instance of an object.
        obj = extract_data_from_fchk_file_for_numerical_derivation(os.path.join(folder_path, i))
        list_with_data_from_files.append(copy.deepcopy(obj))                                                                                    #Saving it to a list later to work

    list_with_data_from_files = sorted(list_with_data_from_files, key = lambda elem: elem.e_field[direction_int])                               #Sorting the data according to the values of electric field. 
    names = obj.list_propreties(direction)[0]                                                                                                   #Getting names for the atributes of the attribute of the object
    list_with_data_from_files = [obj.list_propreties(direction)[1] for obj in list_with_data_from_files]                                        #Getting the list of propreties 
    
    np.savetxt("data.csv", list_with_data_from_files, delimiter=",", fmt='%s', header=",".join(str(v) for v in names))
    np.savetxt("data.tab", list_with_data_from_files, delimiter="\t", fmt='%s') 
    return [names, list_with_data_from_files]



def calc_first_derivative(vector_x, f, n_points = 3, step = 1):

    def three_points(i, step, h):
        return (-1*f[i - step]+1*f[i + step])/(2*1.0*(h*step)**1)
    def five_points(i, step, h):
        return (1*f[i-2*step]-8*f[i-1*step]+0*f[i+0]+8*f[i+1*step]-1*f[i+2*step])/(12*1.0*(h*step)**1)
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
    def three_points(i, step, h):
        return (1*f[i-1]-2*f[i+0]+1*f[i+1])/(1*1.0*(h*step)**2)
    def five_points(i, step, h):
        return (-1*f[i-2]+16*f[i-1]-30*f[i+0]+16*f[i+1]-1*f[i+2])/(12*1.0*(h*step)**2)
    map_functions = {"3" : three_points, "5" : five_points}
    f_x = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_x(i, step, h))
        print(f"i is {i}, value of the deriv is {derivative_vector[-1]}")
    return derivative_vector

#def calc_third_derivative(vector_x, f, n_points = 3, step =1):


def print_derivatives(names, list_propreties, index_energy, order = 1, n_points = 3, step = 1):
    map_derivative = {"1" : calc_first_derivative, "2": calc_second_derivative}
    derivative = map_derivative[str(order)]
 
    #Printing energy derivatives

    list_propreties = np.array((list_propreties))     
    eng_arr = derivative(np.float128(list_propreties[:, 1]), np.float128(list_propreties[:, index_energy]), n_points=n_points, step=step)

    while (len(list_propreties[:,2]) - len(eng_arr)) % 2 == 0 and (len(list_propreties[:,2]) - len(eng_arr)) > 0:
        eng_arr = np.insert(eng_arr, 0, -1)
        eng_arr = np.append(eng_arr, -1)
    names.append("Energy_derivative_order_" + str(order) + "_" + str(n_points))
    list_propreties = np.vstack((list_propreties.T, eng_arr)).T
    return [names, list_propreties]


A = get_list_of_propreties_for_fchk_in_a_folder("/Users/petrumilev/Documents/projects_python/project_girona_donostia/fes_fchk", "Z")
A = print_derivatives(A[0], A[1], 2, 1, n_points = 3, step = 1)
A = print_derivatives(A[0], A[1], 2, 2, n_points = 3, step = 1)

np.savetxt("data_2.csv", A[1], delimiter=",", fmt='%s', header=",".join(str(v) for v in A[0]))
np.savetxt("data_2.tab", A[1], delimiter="\t", fmt='%s', header=",".join(str(v) for v in A[0]))