import numpy as np
from itertools import product
import ast
from objects_for_library import Gaussian_File
import os

# Creating an input file for gaussian calculation
# nproc - to specify the number of processos to be used in calculation, mem - to specify the memory to be used in calculation
# file_name = name by which the file will be saved
# geom - Geometry to be used in calculation
# keywords - keywords to be specified to gaussian. A string or a list of word is accepted
# title - title to be used in file
# oldchk = False, an old checkpoint name needs to be indicated, oldchk_file = Name of the old checkpoint file
# chk = False, put True if a chk with the same name as filename needs to be saved, chk_name = Name of the checkpoint file to be used instead
# charge_multiplicity = (0, 1) by default, if specified, another charge and multiplicity will be used
# basis set = False, if smth else, need to be indicated another basis set in form ["Atom1, Atom2, ...", "Basis Set Used"]. Both values are single strings
# wfx = False, A wfx file name needs to be specified
# Field = False, if smth else, the directions of field need to be specified
#


def create_gaussian_file(file_name, keywords, nproc=False, mem=False, title="Job Name", oldchk=False, oldchk_file=None, chk=False, chk_name=False,
                         charge_multiplicity=(0, 1), geom=False, basis_set=False, wfx=False, Field=False):
    
    file_gaussian = open(file_name, "w")  # Opening the file

    if nproc:  # Adding the line of nprocessors if the number of processors is specified
        file_gaussian.write("%nproc=" + str(nproc) + "\n")

    if mem:  # Adding the line with memory
        file_gaussian.write("%mem=" + mem + "\n")

    if oldchk:  # Checking if and old checkpoint is to be used in the calculation
        if oldchk_file == None:
            raise TypeError(
                "Old checkpoint file is not specified. Working filename is: " + file_name)
        # Adding the line of an old chk to the gaussian input
        file_gaussian.write("%oldchk=" + oldchk_file + "\n")

    if chk:  # Checking if the checkpoint needs to be created
        if chk_name:  # Case when name of chk is different from file name
            file_gaussian.write("%chk=" + chk_name + "\n")
        else:  # Chk point is the same as file name
            file_gaussian.write(
                "%chk=" + file_name[:-4].split("/")[-1] + ".chk\n")

    # Adding the keywords to the file

    if type(keywords) == list:  # Checking if keywords are specified as a list
        new_line = " ".join(keywords)
        file_gaussian.write(new_line + '\n\n')
    elif type(keywords) == str:  # Checking if keywords are specified as a string
        file_gaussian.write(keywords + "\n\n")
    else:
        # An error for the case of wrong keyword list
        raise TypeError(
            "keywords need to be a list of keywords or a string. Working filename is: " + file_name)

    file_gaussian.write(title + "\n\n")  # Adding the title

    # Adding charge and multiplicity. By default 0 1
    # The bloc of code checks if it was introduced as string, or as a list/tuple. 

    if isinstance(charge_multiplicity, str):     
        file_gaussian.write(charge_multiplicity + "\n")
    elif isinstance(charge_multiplicity, tuple) or isinstance(charge_multiplicity, list):
        file_gaussian.write(" ".join(str(x) for x in charge_multiplicity) + "\n")                  #Separating values of a list with a underline, and writing to the file. 
    else: file_gaussian.write("0 1" + "\n")                                                        #If they have not been specified, or there is an error, submit it as (0, 1), which is the most usual case.
    

    #This bloc of code checks if the geometry needs to be added to the file. 

    if geom is not False:  
        for i in range(geom.shape[0]):  # Writting the geometry. Iterating over the lines of the matrix.
            file_gaussian.write(" ".join(geom[i]) + "\n")
        file_gaussian.write("\n")  # Adding a blanc line at the end of file
    else:
        file_gaussian.write("\n")

    #This bloc of code addes an electric field if it has been specified. 

    if Field is not False:  # Adding lines corresponding to the Field
        file_gaussian.write(" ".join([str(x) for x in Field]) + "\n\n")

    if basis_set:  # Adding the lines corresponding to the basis set
        if type(basis_set[0]) == list:  # Checking if the atoms were saved as a list
            file_gaussian.write(" ".join(basis_set[0]) + " 0" + "\n")
        elif type(basis_set[0]) == str:
            file_gaussian.write(basis_set[0] + " 0" + "\n")
        # Writting the basis set in the file
        file_gaussian.write(basis_set[1] + "\n" + "****" + "\n\n")
    if wfx:  # write wfx file
        file_gaussian.write(wfx + "\n\n")
    file_gaussian.close()  # Closing the file
#------------------------------------------------------------------------------------------------------

#Creating a matrix with values of how each element in the electric field changes
#ndim - dimension of matrix 
#type_space - "linear", "log" or "step". Linear - n values on the range of start to finish 
#log - logarithmicaly n spaced values on the range start to finish 
#step - values placed with a specified step from start to finish, finish is not included. 
#all the same = False, change to a [start, finish, step] for the case when for all the directions the change is the same 
#**kwargs submit the directions and how the field will be changing in the form of {"Direction" : [start, finish, step], "Direction2": [start, finish, step]}

def generate_input_energy_field_calculation(ndim, type_space, all_the_same = False, **kwargs):
    ndim_l = [3 for i in range(ndim)]                                                        #Getting the dimensions of the matrix
    matrix = np.zeros(ndim_l, dtype=object)                                                  #Creating a matrix. Having dtype = object is crucial here
    character_mapping = {"X" : "0", "x" : "0", "Y": "1", "y": "1", "Z" : "2", "z": "2"}      #Creating a map of letters into numbers(indexes)
    new_dict = {}                                                                            #To store the new data

    for old_key, value in kwargs.items():                                                    #Changing the letters into number
        for char, replacement in character_mapping.items():                                  #iterating over the map created earlier 
            old_key = old_key.replace(char, replacement)                                     #replacing character
        new_dict[old_key] = value
    
    if all_the_same is not False:                                                            #The case when we want all directions of electric field to have the same values
        if type_space == "linear":
            new_array = np.linspace(all_the_same[0], all_the_same[1], all_the_same[2])
        if type_space == "log":
            new_array = np.logspace(np.log10(all_the_same[0]), np.log10(all_the_same[1]), all_the_same[2])
        if type_space == "step":
            new_array = np.arange(all_the_same[0], all_the_same[1], all_the_same[2])
        for index, element in np.ndenumerate(matrix):     
            print(index, element)
            matrix[index] = new_array
        return matrix

    for key, value in new_dict.items():                                                      #Changing only the elements of the matrix that were specified in the kwargs
        new_key = [int(x) for x in key]                                                      #Making a list of integers from the str
        if type_space == "linear":
            new_array = np.linspace(value[0], value[1], value[2])
        if type_space == "log":
            new_array = np.logspace(np.log10(value[0]), np.log10(value[1]), value[2])
        if type_space == "step":
            new_array = np.arange(value[0], value[1] + 10**(-10), value[2])
        matrix[tuple(new_key)] = new_array                                                   #Assigning the new values 
    return matrix


#------------------------------------------------------------------------------

def generate_gaussian_field_calculation(matrix, file_name, keywords, nproc=False, mem=False, title="Job Name", oldchk=False, oldchk_file=None, chk=False, chk_name=False,
                         charge_multiplicity=(0, 1), geom=False, basis_set=False, wfx=False, Field=False):
    

    #The matrix will be reshaped in a linear matrix.
    #Therefore, we need a mapping between position in orginal matrix, and reshaped one.

    def create_mapping_from_n_dim_to_one_dim(matrix_for_mapping):                       
        mapping = {}                #Dictionary to save the mapping. 

        it = np.nditer(matrix_for_mapping, flags=["multi_index", "refs_ok"])              #Iteration over all values of matrix. 

        i = 0                                                                             #Index in the reshaped matrix. 
        while not it.finished:                                                            #Loop to iterate over all the matrix.
            index = it.multi_index                                                        #Get the index in the original matrix. 
            mapping[str(i)] = index                                                       #Creating a map of index in reshaped matrix as a key, and index in orginal matrix as its value. 
            it.iternext()                                                                 #Going to next value in the original matrix. 
            i += 1                                                                        #Going to next value in reshaped matrix. 
        return mapping                                                                    #Returning the reshaped matrix. 

    #Reassigning index of the reshaped matrix, to the specific letter, to be used in nameing of the files. 
    
    def map_number_to_direction(j, map_1):
        letter_mapping = {"0" : "X", "1" : "Y", "2" :"Z"}                                 #Mapping of index into letters
        j = str(j)
        new_str = ""
        character_mapping = map_1                                                         #Having a map between the linear index and indexing in the original matrix. 
        j = "".join([str(x) for x in character_mapping[j]])                               #Obtaining the index in original matrix as a tuple, and transforming it into a string without spaces.
        for char in str(j):                                                               #A loop to transform the original indexing into letters.
            if char in letter_mapping:                                         
                new_str += letter_mapping[char]                                           #Using the map to get the letter for the char i in the name
            else: new_str += char                                                         #To avoid errors, if the char is not in the map, to return the character
        return new_str                                                                    #Returning the string

    map_1 = create_mapping_from_n_dim_to_one_dim(matrix)                                  #Creating the map between original matrix and reshaped matrix.
    matrix = np.reshape(matrix, -1)                                                       #Reshaping the matrix into a vector. 

    for i in range(len(matrix)):                                                          #Making into a list all values that are not np.ndarray
        if not isinstance(matrix[i], np.ndarray):                                         #This is important, because otherwise product() function will not work
            matrix[i] = [matrix[i]]

    for i, Field in enumerate(product(*matrix)):                                          #Iterating over all possible combinations of electric fields.
        A = []                                                                            #list to save the valus of electric field, to be saved in the name of the file. 
        for j in range(len(Field)):                                                       #Iterating over elements of an instance of electric field
            if int(Field[j]) == 0:                                                        #To not include 0 values in the name of the file
                continue                                                                  #Skipping the cycle 
            A.append([map_number_to_direction(j, map_1), Field[j]])                       #An element of A constains a list containing non zero values of field in the following format [*direction of field*, *value of field*]
        add_name_field = ["_".join([str(x1) for x1 in x]) for x in A]                     #joining by "_" all elements in A
        add_name_field = "_".join(add_name_field) 
        #Creating the respective Gaussian File
        create_gaussian_file(file_name = file_name[:-4] + "_" + "index" + "_" + str(i) + "_" + add_name_field + ".inp", keywords = keywords, nproc=nproc, mem=mem, title=title, oldchk=oldchk, oldchk_file=oldchk_file, chk=chk, chk_name=chk_name,
                         charge_multiplicity=charge_multiplicity, geom=geom, basis_set=basis_set, wfx=wfx, Field=Field)
    return 

#------------------------------------------------------------------------------

def vary_e_field_in_certain_direction(c1, c2, c3, var_range, type_coordinates = "cartesian", type_space = "linear"):
    """
    Function to vary the electric field in a certain direction.
    c1, c2, c3 - coordinates of the point in the space, where the electric field is to be varied. 
    format of the coordinates is (x, y, z) for catesian, (r, theta, phi) for spherical, (r, phi, h) for cylindrical
    Physics convetion is used. Values are to be given in degrees
    The use of (r, theta, phi) denotes radial distance, inclination (or elevation), and azimuth, respectively.
    var_range - range of the variation.
    type_coordinates - "cartesian", "spherical", "cylindrical". Default is cartesian.
    type_space - "linear", "log", "step". Default is linear.

    The function will convert the coordinates in the sphericall coordinates. 
    Then it will vary the radial distance which represents the intensity of the electric field.
    """
    def convert_spherical_to_cartesian_coordinates(r, theta, phi):
        """
        Convert spherical coordinates to cartesian coordinates.
        The use of (r, theta, phi) denotes radial distance, inclination (or elevation), and azimuth, respectively.
        θ the angle measured away from the +Z axis 
        As φ has a range of 360° 
        θ has a range of 180°, running from 0° to 180°
        """
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z
    
    
    def convert_cartesian_to_spherical_coordinates(x, y, z):
        """
        Convert cartesian coordinates to spherical coordinates.
        The use of (x, y, z) denotes the cartesian coordinates.
        """
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r)
        if int(x) == 0:
            phi = np.arctan(np.inf)
        else: phi = np.arctan(y / x)
        return r, theta, phi
    
    def convert_cylindrical_to_spherical_coordinates(r, phi, h):
        """
        Convert cylindrical coordinates to spherical coordinates.
        The use of (r, phi, z) denotes radial distance, azimuth angle, and height, respectively.
        """
        ro = np.sqrt(r**2 + h**2)   
        if int(h) == 0:
            theta = np.arctan(np.inf)
        else: theta = np.arctan(r / h)   
        return ro, theta, phi

    def return_x_y_z(x, y, z):                                               #Function to return the same coordinates
        return x, y, z

    if type_space == "linear":                                               #Creating the space for the variation
        space = np.linspace(var_range[0], var_range[1], var_range[2])
    elif type_space == "step":
        space = np.arange(var_range[0], var_range[1] + var_range[2], var_range[2])
    elif type_space == "log":
        space = np.logspace(np.log10(var_range[0]), np.log10(var_range[1]), var_range[2])
    else: space = np.linspace(var_range[0], var_range[1], var_range[2])

    #Mapping the function to the corresponding conversion of coordinates
    map_function = {"cartesian" : convert_cartesian_to_spherical_coordinates, "spherical" : return_x_y_z, "cylindrical" : convert_cylindrical_to_spherical_coordinates}
    f = map_function[type_coordinates]
    return_vector = []
    if type_coordinates != "cartesian":
        c2 = np.radians(c2)                               #Converting from degrees to radians
        c3 = np.radians(c3)
    r, theta, phi = f(c1, c2, c3)                         #Converting the coordinates to spherical
    for i in space:                                       #Obtaining the new values for electric field
        r = i                                             #Length of vector is changed
        x, y, z = convert_spherical_to_cartesian_coordinates(r, theta, phi)        #Obtaining the new cartesian coordinates to be used in the Gaussian input file.
        x, y, z = np.round((x, y, z), 10)                                          #Rounding the values to 10 decimal places
        return_vector.append((x, y, z))                                            #Appending the new values to the list
    return return_vector


#-------------------------------------------------------------------------------------------------------------------------

def start():

    File_Info = Gaussian_File()      #Creating an object to save the data introduced.
    separator = "\n-------------------------------------------------------------------"
    File_Info.file_name = input("\n1. Introduce the name of the file of your calculation. \nIncluding the path. If not, the files will be saved in the directory were this file is.\nExample /Users/User/Documents/Gaussian/Folder/File_name.inp\nIntroduce name of the file here: ")
    print(separator)
    #----------------------------------------------------------------------------------------------------------------------------------
    a = [] 
    i = 1 
    while True:
        #A cycle to introduce as many keywords as is desired. 
        keyword = input("\n2. Introduce the keywords. Each line is a new line for the keyword.\n\nIntroduce 0 to finish the introduction of keywords.\nIntroduced the desired line here: ")
        if keyword == "0":
            break
        a.append(keyword)
        print("-----------------")
        print("Full list of keywords introduced so far is:")
        print("\n".join(a))
        print("-----------------")
        print("Lines introduced", i)
        print("-----------------")
        i += 1
    File_Info.keywords = "\n".join(a)
    print(separator)
    #-------------------------------------------------------------------------------------------------------------------------------
    try:
        nproc = int(input("\n3. Introduce the number of processors to be used during the calculation.\n\nIntroduce 0 if you do not want to specify the number of processors.\n\nNumber of processors used is: "))
        if nproc != 0:
            File_Info.nproc = nproc
        else: File_Info.nproc = False
    except ValueError:
        print("\nInvalid input. Please enter and integer. 0 if you do not wish to specify the number of processors. Introduce False\n")
    print(separator)
    mem = input("\n4. Introduce the amount of memory to be used during the calculation. Also indicate the amount. Example: 100MB. \nIf you do not want to specify the memory, leave the space blank. (i.e., press Enter)\n\nThe ammount of memory to be used during the calculation: ")
    if not bool(mem):
        mem = False
    File_Info.mem = mem
    print(separator)
    #----------------------------------------------------------------------------------------------------------------------------------
    a = [] 
    i = 1 
    while True:
        line = input("\n5. Introduce title/comment for the job. Each line is a new line for the title/comment.\n\nIntroduce 0 to finish the introduction.\n\nTitle: ")
        if line == "0":
            break
        a.append(line)
        print("-----------------")
        print("Full list of title/comments introduced so far is:")
        print("\n".join(a))
        print("-----------------")
        print("Lines introduced", i)
        print("-----------------")
        i += 1
    File_Info.title = "\n".join(a)
    print(separator)
    #-------------------------------------------------------------------------------------------------------------------------------

    oldchk = input("\n6. Do you want to use an old chk file? Y/N\n")
    if oldchk == "":
        oldchk = False
    elif oldchk[0].lower() == "y":
        oldchk = True
        File_Info.oldchk = oldchk
        File_Info.oldchk_file = input("\nIntroduce the name for the old chk file, including the extension.\n\nOldchk file name is: ") 
    else: oldchk = False
    
    print(separator)

    geometry_path = input("\n7. Introduce path for geometry coordinates. \nLeaving this space blank will result in not submiting geometry coordinates to the gaussian input file.\n\nPath for the geometry is: ")
    if not geometry_path:
        geometry_path = False
    else: File_Info.geom = np.loadtxt(geometry_path, dtype = str)

    print(separator)
    
    chk = input("\n8. Do you want to save an chk file for this calculation? Yes/No\n")
    if chk == "":
        chk = False
    elif chk[0].lower() == "y":
        File_Info.chk = True
        chk_name = input("\nIntroduce the chk file name. \nLeaving it blank will result in using the same name for chk as for the log file\n")
        if not bool(chk_name):
            chk_name = False
        else: File_Info.chk_name = chk_name
    else: chk = False

    print(separator)
    
    File_Info.charge_multiplicity = input("\n9. Intorduce charge and multiplicity of the system. \nTwo integers separated by space are to be introduced. \nExample: 0 1\n\nCharge and multiplicity which will be used in calculation is: ")
    
    print(separator)

    basis_set_atoms = input("\n10. Introduce atoms for which basis set is to be specified.\nAtoms are to be separated by spaces. \nExample: Li C N O \n\nLeave blank if you do not want to specify basis set for atoms\n\nAtoms for which basis set is specified are: ")
    if bool(basis_set_atoms):
        basis_set_name = input("\nIntroduce the name for the basis set to be used\n\nName of the basis set is: ")
        File_Info.basis_set_gaussian = [basis_set_atoms, basis_set_name]
    else: File_Info.basis_set_gaussian = False
    print(separator)
    wfx = input("\n11. Do you want to save an wfx file? Indicate the name of the file. Leave blank if you do not wish to print wfx\n\nName of the file: ")
    if not bool(wfx):
        wfx = False
    File_Info.wfx = wfx
    print(separator)
    Energy = input("\n12. Do you want/have to specify a electric field for this calculation? Y/N\n")
    if Energy.lower()[0] == "y":
        type_energy_variation = input("What type of energy calculation do you want to specify?\n1.Indicate a single value for the field. \n2.Indicate a direction in which you want to vary the field. \n3 Create a grid/mesh of values for the field. \n\nIntroduce the corresponding integer: ")
        if type_energy_variation == "1":
            #The case when only one value of electric field is to be used.
            field = input("\nIntroduce the value of the electric field. \nExample: 0.0001, 0, 0\n\nValue of the electric field is: ")
            File_Info.Field = field
            create_gaussian_file(File_Info.file_name, File_Info.keywords, nproc = File_Info.nproc, mem = File_Info.mem, title = File_Info.title, oldchk= File_Info.oldchk, oldchk_file=File_Info.oldchk_file, chk = File_Info.chk, chk_name=File_Info.chk_name, charge_multiplicity=File_Info.charge_multiplicity, geom = File_Info.geom, basis_set = File_Info.basis_set_gaussian, wfx = File_Info.wfx, Field = File_Info.Field)
        elif type_energy_variation == "2":
            #The case when the electric field is to be varied in a certain direction.
            print("Provide the following information separated by commas (,)\n")
            print("c1, c2, c3, start, finish, step, type_coordinates, type_space")
            print("c_i are coordinates in the desired type of coordinates.\nx, y, z for cartesian\nr, theta, phi for spherical\nr, phi, h for cylindrical\n start - starting range of the variation\nfinish - ending range of the variation\nstep - step of the variation\n type_coordinates - cartesian, spherical, cylindrical\n type_space - linear, log, step")
            print("Values are to be given in degrees if it is the case")
            print("Example: 0, 0, 180, -5, 5, 1, spherical, step")
            info = input("Provide the following information separated by commas (,)\n")
            info = info.split(",")
            info = [x.strip() for x in info]
            e_field_range = vary_e_field_in_certain_direction(float(info[0]), float(info[1]), float(info[2]), [float(info[3]), float(info[4]), float(info[5])], type_coordinates = info[6], type_space = info[7])
            for i, field in enumerate(e_field_range):
                combined_name = "_index_" + str(i) + "_X_" + str(field[0]) + "_Y_" + str(field[1]) + "_Z_" + str(field[2]) + ".inp"
                create_gaussian_file(File_Info.file_name[:-4] + combined_name, File_Info.keywords, nproc = File_Info.nproc, mem = File_Info.mem, title = File_Info.title, oldchk= File_Info.oldchk, oldchk_file=File_Info.oldchk_file, chk = File_Info.chk, chk_name=File_Info.chk_name, charge_multiplicity=File_Info.charge_multiplicity, geom = File_Info.geom, basis_set = File_Info.basis_set_gaussian, wfx = File_Info.wfx, Field = field)
        elif type_energy_variation == "3":
            type_energy = int(input("\nHow do you want your energy to vary? \nPossible choices: \n\n1. Linearly (i.e., a given number of points equally spaced on the given interval), \n2. Step (i.e., an unknown number of points, separated by a specified step on a given interval), \n3. Logarithmicaly. (i.e., A specified number of points, separated logarithmically (base 10), on a given interval)\n\nIntroduce the corresponding integer: "))
            if type_energy == 1:
                type_energy = "linear"
            elif type_energy == 2:
                type_energy = "step"
            elif type_energy == 3:
                type_energy == "log"
            else: type_energy = "linear"
            print(separator)
            ndim = int(input("\nIntroduce number of dimension for the energy calculation. \n\nn = 1 corresponds to only X, Y, and Z. n = 2 corresponds to XX, YY, etc.\n\nIntroduce number of dimension: "))
            print(separator)
            dict_direct = ast.literal_eval("{" + input("\nIntroduce the directions for which you would like to perform the calculations.\nFormat for this is:\
                            \n\n'XX':[start, finish, step/number of points], 'XZ' : [start, finish, number of points], etc\n\nRespecting the format above is crucial. The direction should correspond with number of dimensions. 'X' for dimension 1, 'XX' for dimension 2, etc. \
                            \n\nIntroduce the points: ") + "}")
            field_matrix = generate_input_energy_field_calculation(ndim, type_energy, **dict_direct)
            generate_gaussian_field_calculation(field_matrix, File_Info.file_name, File_Info.keywords, nproc = File_Info.nproc, mem = File_Info.mem, title = File_Info.title, oldchk= File_Info.oldchk, oldchk_file=File_Info.oldchk_file, chk = File_Info.chk, chk_name=File_Info.chk_name, charge_multiplicity=File_Info.charge_multiplicity, geom = File_Info.geom, basis_set = File_Info.basis_set_gaussian, wfx = File_Info.wfx)
        else: print("There was a mistake while specifying the field. Please try again.")
    else: create_gaussian_file(File_Info.file_name, File_Info.keywords, nproc = File_Info.nproc, mem = File_Info.mem, title = File_Info.title, oldchk= File_Info.oldchk, oldchk_file=File_Info.oldchk_file, chk = File_Info.chk, chk_name=File_Info.chk_name, charge_multiplicity=File_Info.charge_multiplicity, geom = File_Info.geom, basis_set = File_Info.basis_set_gaussian, wfx = File_Info.wfx)
    return File_Info
#--------------------------------------------------------------------------

def update_oldchk_for_files_in_a_folder(folder_path, file_extension = ".com", reference = False):
    """
    This function updates the %oldchk= line in the Gaussian input files in a folder.
    :param folder_path: the path to the folder containing the Gaussian input files
    :param file_extension: the extension of the Gaussian input files
    :param reference: the name of the reference file
    :return: None

    If reference is False, the files are referenced to the file n-1 according to the value of the e field
    """

    def change_oldchk_file(file_path, new_oldchk_name):                # This function changes the %oldchk= line in a Gaussian input file
        old_chk_line = "%oldchk="                                      # The function takes the path to the file and the name of the new chk file
        with open(file_path, "r") as file_gaussian:                    
            lines = file_gaussian.readlines()
        for i, line in enumerate(lines):
            if old_chk_line in line.lower():
                lines[i] = "%oldchk=" + str(new_oldchk_name) + "\n"
                with open(file_path, "w") as file_1:
                    file_1.writelines(lines)
                break

    file_list = os.listdir(folder_path)                    # This part of the function sorts the files in the folder by the number in the file name     
    file_list = [file_name for file_name in file_list if file_name.endswith(file_extension)]
    file_list = [(np.float64(x.split("_")[-1][1:-4]), x) for x in file_list]  # The number is the last part of the file name, after the last underscore and before the file extension
    file_list = sorted(file_list, key=lambda x: x[0])                   # The files are sorted by the number
    zero_index = None                                                   # The index of the file with the number 0 is found
    for i in file_list:
        if np.round(i[0],0) == 0:
            zero_index = file_list.index(i)                            # The index of the file with the number 0 is found
            break
    file_list = [x[1] for x in file_list]                               # The file names are extracted from the list of tuples
    if reference is False:                                             # If no reference file is given, all the files are referenced to the file n-1
        reference = file_list[zero_index]
        for i in range(zero_index+1, len(file_list)):                   
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference = file_list[i]
        reference = file_list[zero_index]
        for i in range(zero_index-1, -1, -1):
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference= file_list[i]
    return


#-------------------------------------------------------------------------------------------------------------------------

def create_mapping_from_n_dim_to_one_dim(matrix_for_mapping):                       
        """
        This functions returns a map of the index in the reshaped matrix as a key, and index in the original matrix as its value.
        Original matrix can be n-dimensional matrix.
        """
        mapping = {}                                                                      #Dictionary to save the mapping. 

        it = np.nditer(matrix_for_mapping, flags=["multi_index", "refs_ok"])              #Iteration over all values of matrix. 

        i = 0                                                                             #Index in the reshaped matrix. 
        while not it.finished:                                                            #Loop to iterate over all the matrix.
            index = it.multi_index                                                        #Get the index in the original matrix. 
            mapping[str(i)] = index                                                       #Creating a map of index in reshaped matrix as a key, and index in orginal matrix as its value. 
            it.iternext()                                                                 #Going to next value in the original matrix. 
            i += 1                                                                        #Going to next value in reshaped matrix. 
        return mapping 


def map_number_to_direction(j, map_1):
    letter_mapping = {"0" : "X", "1" : "Y", "2" :"Z"}                                 #Mapping of index into letters
    j = str(j)
    new_str = ""
    character_mapping = map_1                                                         #Having a map between the linear index and indexing in the original matrix. 
    j = "".join([str(x) for x in character_mapping[j]])                               #Obtaining the index in original matrix as a tuple, and transforming it into a string without spaces.
    for char in str(j):                                                               #A loop to transform the original indexing into letters.
        if char in letter_mapping:                                         
            new_str += letter_mapping[char]                                           #Using the map to get the letter for the char i in the name
        else: new_str += char                                                         #To avoid errors, if the char is not in the map, to return the character
    return new_str                                                                    #Returning the string


def read_input_for_electric_field_from_file_and_generate_files(path_to_file, extension = ".com"):
    """
    Function to generate Gaussian input files for the calculation of the electric field from a template file.
    Template will be specified in the manual.
    This funciton can generate files for the case when the electric field is varied in one specific direction or 
    it can generate a grid over a space. 
    This function is using the four following function:
    generate_input_energy_field_calculation(ndim, type_space, all_the_same = False, **kwargs)
    vary_e_field_in_certain_direction(c1, c2, c3, var_range, type_coordinates = "cartesian", type_space = "linear")
    create_mapping_from_n_dim_to_one_dim(matrix)
    map_number_to_direction(i, map_directions)
    """                                       

    def change_chk_file(file_path, new_oldchk_name):
        old_chk_line = "%chk="
        with open(file_path, "r") as file_gaussian:
            lines = file_gaussian.readlines()
        for i, line in enumerate(lines):
            if old_chk_line in line.lower():
                lines[i] = "%oldchk=" + str(new_oldchk_name) + "\n"
                print(lines[i])
                with open(file_path, "w") as file_1:
                    file_1.writelines(lines)
                break

    type_electric_field_calculation = 0
    input = 0
    is_recording_file = True                                           #Boolean to indicate if we are recording the file
    is_recording_e_field = False                                       #Boolean to indicate if we are recording the electric field
    count = 0                                                          #To get the value where we will be inserting electric field
    lines = []                                                         #Saved lines of the file
    with open(path_to_file, "r") as file:                              
        for line in file:
            if line.strip() == "***Start_e_field***":                  #Looking for the start of the desired section so that we can get the input data
                is_recording_e_field = True                            #Boolean to let us read input data
                is_recording_file = False                              #Stop recording file lines to be in the final file
                line_to_introduce_e_field = count - 1
            if is_recording_file:                                      #Recording the lines of the file
                lines.append(line)
            if is_recording_e_field:                                   #Recording the input data
                if "#Corresponding" in line:                           #Read the type of calculation
                    type_electric_field_calculation = int(line.strip().split(" ")[-1])
                if "#Input" in line:                                   #Read input data
                    input = [x for x in line.strip().split(" ")[1:]]
            if line.strip() == "***Finish_e_field***":                 #Look for the finish of the block of reading the input data.
                is_recording_e_field = False                           #Stop recording input data
                is_recording_file = True                               #Continue recording the file
            count += 1                                                 #Counting the lines of the file
    print(type_electric_field_calculation)
    if type_electric_field_calculation == 1:                           #If recording the variation of electric field in one direction
        map_directions = {"0" : "X", "1" : "Y", "2" :"Z"}              #Dictionary to map the index of the direction into the letter
        #Generate the values of the electric field over the specified direction
        e_fields = vary_e_field_in_certain_direction(float(input[0]), float(input[1]), float(input[2]), var_range = [float(input[3]), float(input[4]), int(input[5])], type_coordinates = input[6], type_space = input[7])
        for field in e_fields:
            if field[0] == 0 and field[1] == 0 and field[2] == 0:
                continue
            else: directions = [map_directions[str(i)] for i, x in enumerate(field) if x != 0]
        for field in e_fields:                                         #Looping to creating the files
            #Creating the name of the file. File name will have the following format:
            #Input_kw example_test_X-1.41e+00_Y-1.41e+00
            if field[0] == 0 and field[1] == 0 and field[2] == 0:
                file_name  = path_to_file[:-4] + "_" + "_".join([str(x) + "+0" for x in directions]) + extension
            else: file_name = path_to_file[:-4] + "_" + "_".join(["".join((map_directions[str(i)], "+" + "{:.2e}".format(x) if x > 0 else "{:.2e}".format(x))) for i, x, in enumerate(field) if x!= 0]) + extension
            with open (file_name, "w") as file:                        #Creating the file
                count = 0                                              #Counting lines of the file
                for line in lines:                                     #Writting line of the file
                    file.write(line)
                    if count == line_to_introduce_e_field:             #Add value of e_field in the specified line
                        file.write(" ".join([str(x) for x in field]) + "\n")
                    count += 1
            change_chk_file(file_name, file_name.split("/")[-1][:-4] + ".chk")
    elif type_electric_field_calculation == 2:                         #Case of generating a grid over the space of the electric field. But can also be generated grids in n dimensions
        input[2] = True if input[2].lower() == "y" else False          #Having all the values the same
        input[3] = ast.literal_eval(input[3])                          #Reading the directions
        #Generating the matrix of how the electric field will vary. A position in the matrix corresponds to a direction.
        matrix = generate_input_energy_field_calculation(int(input[0]), input[1], input[2], **input[3])     
        #Creating a map of directions from n dimensions to one dimension
        #The resulting dictionary has the form {'0': (0, 0), '1': (0, 1), '2': (0, 2), ...}
        map_directions = create_mapping_from_n_dim_to_one_dim(matrix)
        matrix = np.reshape(matrix, -1)
        for i in range(len(matrix)):    #Make all non_list elements into a list. This is important for the product function.
            if not isinstance(matrix[i], np.ndarray):
                matrix[i] = [matrix[i]]
        for field in product(*matrix):  #Looping over all the possible combinations of the electric field. product function is used to get all the combinations.
            #File name will be of the following format: 
            #Input_kw example_test_X+1.41e+00_Y+1.41e+00
            file_name = path_to_file[:-4] + "_" + "_".join(["".join((map_number_to_direction(i, map_directions), "+" + "{:.2e}".format(x) if x > 0 else "{:.2e}".format(x))) for i, x, in enumerate(field) if x!=0]) + extension
            with open (file_name, "w") as file:                #Creating the files with the specified name and e field
                count = 0
                for line in lines:
                    file.write(line)                           #Writting the lines of the file
                    if count == line_to_introduce_e_field:     #Writting the e field in the specified line
                        file.write(" ".join([str(x) for x in field]) + "\n")
                    count += 1
    return type_electric_field_calculation, input

def add_keywords(path_file, *kw):
    """Add keywords to a Gaussian input file.
    
    Parameters
    ----------
    path_file : str
        Path to the Gaussian input file.
    *kw : str
        Keywords to be added to the Gaussian input file.

    Function check if the keyword is in the file, if not, it will add it.
    """
    kw_found = {word: False for word in kw}                             #Generating a dictionary which will keep info about which kws we need to add
    check_lines_for_kw = False                                          #Flag to check if we are in the part of the file where we need to check for kws
    added_kw = []                                                       #List of kws which need to be added (bcz they are not in the file)
    kw_have_not_been_added = True                                       #Flag to check if we have added the kws only once. It is to allow for multiple use of hashtag
    with open(path_file, "r") as f:
        lines = f.readlines()                                           #Read the file and save it as a list of lines
    with open(path_file, "w") as f:
        for line in lines:                                              #Loop over the lines of the file
            if line.startswith("#") and kw_have_not_been_added:         #If the line starts with hashtag, we need to check for kws
                check_lines_for_kw = True                              
            if check_lines_for_kw:                                      #If we are in the part of the file where we need to check for kws
                for word in kw:
                    if word in line:
                        kw_found[word] = True                           #If the kw is in the line, we change the value of the kw_found dictionary to True
            if line.strip() == "" and kw_have_not_been_added:           #If we have reached the end of the kws part of the file, we generate a list of kw that need to be added
                check_lines_for_kw = False
                added_kw = [key for key, value in kw_found.items() if not value]
            if added_kw and kw_have_not_been_added:                     #If we have kws to add, we add them to the file
                f.write(line.strip())
                f.write(" ".join(added_kw) + "\n\n")
                kw_have_not_been_added = False
            else: 
                f.write(line)
    return

def extract_data_from_fchk_file_for_numerical_derivation(file_path):
    """
    This function extracts "Dipole Moment", "Polarizability", "HyperPolarizability", "Quadrupole Moment" from a function. 
    The result is tuple with (electric field, dict_with values)
    Input is the absolute path to the file. 
    """
    def save_lines_after_keyword(input_file, keyword):                      #Getting the numerical values after the specified keywords
        with open(input_file, "r") as file:                                 #Keywords are Dipole Moment, Hyperpolarizability etc
            for line_number, line in enumerate(file, start = 1):            #Lopping over all the file and searching for line with the keyword
                if keyword in line:                                     
                    imp_line = (line_number, line)                          #Saving number of the line and the line itself
                    break
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
    
    def get_electric_field_values(input_file):                              #A fundtion to get value of electric field, as the previous function does not allow for this.
        with open(input_file, "r") as file:                                 #Oppening the file
            line_n_minus1 = ""
            for line_number, line in enumerate(file, start = 1):            #Looping over lines of the file
                if "External E-field" in line_n_minus1:                     #if in the previous line was the keyword
                    imp_line = (line_number, line.split())                  #than save the line (which is after the keyword and which contains the values for the electric field)
                    break
                line_n_minus1 = line

        e_field_1 = imp_line[1][1:4]                                        #Values of the electric field are saved in position 1, 2, 3 of the resulting vector 
        e_field_1 = [np.float128(x) for x in e_field_1]                     #Converting str to an appropriate numerical value
        return e_field_1                                                    
        
    field = get_electric_field_values(file_path)

    list_kw = ["Dipole Moment", "Polarizability", "HyperPolarizability", "Quadrupole Moment"]
    resulting_dict = {}
    for i in list_kw:                                                       #Getting actual values
        resulting_dict[i] = save_lines_after_keyword(file_path, i)
    return (field, resulting_dict)