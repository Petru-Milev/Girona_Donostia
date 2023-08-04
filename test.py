import numpy as np
import os
import re
from functions_for_library import *

def change_kw(path_to_file, keywords):
    """
    This function will change the keywords in a given file to the ones specified
    """
    with open(path_to_file, "r") as file:
        lines = file.readlines()                            #Reading the lines of the file
    with open(path_to_file, "w") as file:
        introducing_new_kw = False
        gaussian_file_started = True
        count_kw_introduced = 0
        for line in lines:
    
            if "#" in line.strip() and gaussian_file_started:               #Looking for the section in input where keywords are specified
                introducing_new_kw = True

            if introducing_new_kw:                                          #Introducing new keywords if the kw section was found
                if count_kw_introduced == 0:                                #Introducing once the words   
                    for i, line in enumerate(keywords):                     
                        file.write(line + "\n")
                    gaussian_file_started = False                           #Not introducing keywords from Gaussian file
                    count_kw_introduced += 1
                if line.strip() == "":                                      #Looking for the end of section where kw are specified 
                    introducing_new_kw = False
                    gaussian_file_started = True
            if gaussian_file_started:                                       #Introducing all the Gaussian file lines before and after the keywords section
                file.write(line)
    return 

def read_input_file(path_to_file, extension = ".com"):
   
    from itertools import product

    def split_text_for_inp(text):
        """
        This function will separate words in the line which has multiple brackets
        This: 'update_old_chk(n-1) basis_set(origin) read_geom() new_kw'
        Will be separate into this: ['update_old_chk(n-1)', 'basis_set(origin)', 'read_geom()', 'new_kw']
        """
        result = ""
        parens_open = 0
        for char in text:
            if char =='(':
                parens_open += 1
            elif char == ')':
                parens_open -= 1
            if char == ',' and parens_open == 0:
                char = ""
            if char == ' ' and parens_open == 0:
                print(char)
                char = ";"
            result += char
        return result.split(";")
    
    def get_inp_text(text):
        result = ""
        parens_open = 0
        to_return = []
        for char in text:
            if char == ")":
                parens_open -= 1
            if parens_open > 0:
                result += char
            if char =='(':
                parens_open += 1
            if result != "" and parens_open == 0:
                to_return.append(result)
                result = ""
        if len(to_return) == 0:
            return None
        else: return to_return

    def generate_files_e_field_in_one_direction(path_to_file, c1, c2, c3, start, finish, step, type_coordinates, type_space, extension = ".com", lines = "" ,new_kw = False):
        """
        This function will generate files with different electric field all being aligned in one specified direction
        c1, c2, c3, coordinates of the direction, it can be either cartesian, spherical or cylindrical
        start, finish, step, the range of the electric field
        type_coordinates - "cartesian", "spherical" or "cylindrical"
        type_space - "linear", "step" or "log"
        extension - the extension of the file
        lines - Gaussian Input text to be written
        new_kw - list of new keywords to be added to the file
        more detailed about the function can be found in descripton of the function gen_e_field_direction
        """
        c1, c2, c3 = np.float128(c1), np.float128(c2), np.float128(c3)
        start, finish = np.float128(start), np.float128(finish)
        if type_space == "linear":
            step = int(step)
        elif type_space == "log":
            step = int(step)
        else: step = np.float128(step)
        map_directions = {"0" : "X", "1" : "Y", "2" :"Z"}              #Dictionary to map the index of the direction into the letter
        #Generate the values of the electric field over the specified direction
        e_fields = vary_e_field_in_certain_direction(c1, c2, c3, var_range = [start, finish, step], type_coordinates = type_coordinates, type_space = type_space)
        for field in e_fields:
            if field[0] == 0 and field[1] == 0 and field[2] == 0:
                continue
            else: directions = [map_directions[str(i)] for i, x in enumerate(field) if x != 0]  #Getting the directions of the electric field to be used in nameing of the files
        
        dont_add_chk_last_file = False                                                   #Flag to not add ChkBasis, geom=check, guess=(read), GFInput to the last file, for case when we have only negative values of the electric field
        for count, field in enumerate(e_fields):                                         #Looping to creating the files
            #Creating the name of the file. File name will have the following format:
            #Input_kw M062X_101_Z+0.001900.com
            if field[0] == 0 and field[1] == 0 and field[2] == 0:
                file_name  = path_to_file[:-4] + "_" + "_".join([str(x) + "+0" for x in directions]) + extension 
            else: file_name = path_to_file[:-4] + "_" + "_".join(["".join((map_directions[str(i)], "+" + "{:.6f}".format(x) if x > 0 else "{:.6f}".format(x))) for i, x, in enumerate(field) if x!= 0]) + extension
            
            with open (file_name, "w") as file:                        #Creating the file                           
                for line in lines:                                     #Writting line of the file
                    file.write(line)
                if field[0] == 0 and field[1] == 0 and field[2] == 0:  #If 0 field, it will not write the field
                    None
                else: 
                    file.write("\n\n" + " ".join(["{:.6f}".format(x) for x in field]) + "\n\n")
            change_line_in_file(file_name, "%chk", "%chk=" + file_name.split("/")[-1][:-4] + ".chk")    #Adding the checkpoint file name
            if new_kw:
                if field[0] == 0 and field[1] == 0 and field[2] == 0:
                    None                                               #Keywords for 0 field will be from the gaussian input file
                else:                                                  #Changing the keywords for the ones specified in the respective section
                    change_kw(file_name, new_kw)
            if field[0] == 0 and field[1] == 0 and field[2] == 0:      #Insering geometry for 0 field
                insert_geom(file_name, path_to_geom)
                None
            else:
                if "automatically_update_kw" in kw_without_input_for_function:      #Checking the keyword for the field calculation
                    add_keywords(file_name, *["IOp(3/14=-6)"])
                index_update_old_chk = kw_without_input_for_function.index("update_old_chk")
                type_old_chk_kw = input_for_function[index_update_old_chk]          #Getting info about how we update old chk file
                if (0, 0, 0) in e_fields:                                           #Studying the case when we have 0 field
                    if ("automatically_update_kw" in kw_without_input_for_function) and (type_old_chk_kw[0] == "zero" or type_old_chk_kw[0] == "n-1"):
                        add_keywords(file_name, *["ChkBasis", "geom=check", "guess=(read)", "GFInput"])
                        with open(log_file, "a") as log:
                            log.write("Checked and added if they were missing the following keywords: ChkBasis, geom=check, guess=(read), GFInput to " + file_name + "\n")
                else:                                                               #Studying the case when we do not have 0 field, and we need to choose a file from the boundary
                    if count == 0:
                        if ("_X+" in file_name) or ("_Y+" in file_name) or ("_Z+" in file_name):
                            #Checking that we have only positive values of the electric field
                            #If this is the cases, for the first iteration we will not add kw to the file
                            #Because we will make references to the lower boundary files
                            #!!!Posible bugs!!!
                            None
                        else:
                            #If we have negative values of the electric field, we will add the kw to the first file
                            add_keywords(file_name, *["ChkBasis", "geom=check", "guess=(read)", "GFInput"])
                            dont_add_chk_last_file = True   #Bcz we did not use first file as a reference, we will use the last one
                            with open(log_file, "a") as log:
                                log.write("Checked and added if they were missing the following keywords: ChkBasis, geom=check, guess=(read), GFInput to " + file_name + "\n")

                    else: 
                        if count == (len(e_fields)-1) and dont_add_chk_last_file:
                            #Checking if we need to add kw to the last file
                            None
                        else:
                            add_keywords(file_name, *["ChkBasis", "geom=check", "guess=(read)", "GFInput"])
                            with open(log_file, "a") as log:
                                log.write("Checked and added if they were missing the following keywords: ChkBasis, geom=check, guess=(read), GFInput to " + file_name + "\n")
            insert_geom(file_name, path_to_geom) #Adding geometry to the created file. This function will check if there are kw that dont permit specification of the geometry
        
    def check_double_lines(folder):
        #Check if there are two consecutive lines that are whitespace
        folder_list = os.listdir(folder)
        folder_list = [x for x in folder_list if x.endswith(extension)]
        for file in folder_list:
            with open(os.path.join(folder, file), "r") as f:
                lines = f.readlines()
            with open(os.path.join(folder, file), "w") as f:
                previous_line = ""
                for line in lines:
                    if (line.strip() == "") and (previous_line.strip() == ""):
                        previous_line = line.strip()
                        continue
                    else: f.write(line)
                    previous_line = line.strip()
                #Making that files end in a double lines
                if previous_line == "":
                    f.write("\n")
                else: f.write("\n\n")
    
    def insert_geom(path_to_file, path_to_geom):
        """
        This funciton is inserting the geometry into the file
        path_to_file - path to the file
        path_to_geom - path to the geometry file, if specified "delete" it will not introduce the geometry into the file, and will delete the respective line
        The function will automatically check with keywords dont allow for the introduction of the geometry
        """
        if path_to_geom == None:
            return
        
        with open(path_to_file, "r") as file:
            lines = file.readlines()
        for line in lines:
            #Checking for the keywords that dont allow for the introduction of the geometry
            if "geom=check" in line:
                path_to_geom = "delete"
                break
            if "guess=(read)" in line:
                path_to_geom = "delete"
                break
        
        #deleting the line of geometry if this is necesary
        if path_to_geom == "delete":
            with open(path_to_file, "r") as file:
                lines = file.readlines()
            with open(path_to_file, "w") as file:
                for line in lines:
                    if "@" in line.strip():
                        continue
                    file.write(line)
            return
        #introducing the geometry into the file if @ is present
        with open(path_to_file, "w") as file:
            for line in lines:
                if "@" in line.strip():
                    with open(path_to_geom) as geom_file:
                        geom = geom_file.readlines()
                    file.write("".join(geom))
                    continue
                file.write(line)
        return

    def read_block_in_file(path_to_file, kw_start):
        """
        This function will read the block of text between two keywords
        """
        with open(path_to_file, "r") as file:
            lines = []
            record = False
            count = 0
            for line in file:
                if kw_start in line.strip() and count == 0:
                    record = True
                    count += 1
                    continue
                if record:
                    if kw_start in line.strip():
                        record = False
                        break
                    else: lines.append(line.strip())
        return lines
    
    path_to_folder = "/".join(path_to_file.split("/")[:-1])     #Getting the path to the folder
    original_file_name = path_to_file.split("/")[-1]            #Getting the name of the file
    log_file = path_to_file[:-4] + "_WARNINGS_log.txt"          #Creating the log file

    with open(log_file, "w") as file:
        file.write("All the critical errors will be updated here: " + path_to_file + "\n\n")

    with open(path_to_file, "r") as file:
        #This part extracts the keywords to be used by this function
        kw_lines = []
        for i, line in enumerate(file):
            if line.strip() == "":
                line_kw_end = i
                break
            else: kw_lines.append(line.strip())
    keywords = []
    #This will get the list of all keywords for this function and their options specified in the input 
    for line in kw_lines:
        keywords.extend(split_text_for_inp(line))
    keywords = keywords[1:]
    print("--------------------------------------")
    with open(log_file, "a") as file:
        file.write("Keywords Provided to the input are:\n")
        file.write(" ".join([x for x in keywords]) + "\n")
    print("Keywords Provided to the input are:")
    print(keywords)
    with open(path_to_file, "r") as file:
        #This part will write the original Gaussian file lines
        original_file_lines = []
        record_file = False
        for line in file:
            if "***start_gaussian_file***" in line.strip().lower():
                record_file = True
                continue
            if record_file:
                original_file_lines.append(line)
    kw_without_input_for_function = []                      #Keywords without the their options
    input_for_function = []                                 #Options for the respective kw
    for i in keywords:
        kw_without_input_for_function.append(i.split("(")[0])
        input_for_function.append(get_inp_text(i))

    print("list of keywords: ", kw_without_input_for_function)

    if "read_geom" in kw_without_input_for_function:
        """
        This part will check if the geometry needs to be updated to any of the files, and will extract the path to the geometry
        """
        index = kw_without_input_for_function.index("read_geom")
        inp = input_for_function[index]
        
        with open(path_to_file, "r") as file:
            original_lines = file.readlines()
            for line in original_lines:
                if "@" in line.strip():
                    path_to_geom = line.strip()[1:]
                    break
    else: path_to_geom = None
    print("\n\n", "path to geom: ", path_to_geom)

    if "gen_e_field_direction" in kw_without_input_for_function:
        """
        This part will generate the files with different electric field in one direction
        inp - is the input for the function gen_e_field_direction, it has the following format:
        c1, c2, c3, start, finish, step, type_coordinates, type_space, (not_necessary)extension of the file
        """
        index = kw_without_input_for_function.index("gen_e_field_direction")
        inp = input_for_function[index]
        if inp == None:
            print("No input for function gen_e_field_direction")
            print("Please specify the input for the function gen_e_field_direction")
            print("Syntax: gen_e_field_direction(c1, c2, c3, start, finish, step, type_coordinates, type_space, (not_necessary)extension of the file)")
        new_kw = False
        if "new_kw" in keywords:
            new_kw = read_block_in_file(path_to_file, "kw_e_field_calc")
        inp = inp[0].replace(",", " ").split()
        generate_files_e_field_in_one_direction(path_to_file, *inp, lines = original_file_lines, new_kw=new_kw)
        check_double_lines(path_to_folder)
    
    if "update_old_chk" in kw_without_input_for_function:
        """
        This part will check if the files need to be updated with the old checkpoint file
        and will find the type of the update
        zero - will reference all files to the file with zero field
        n-1 - will reference all files to the previous file. 
        0 field file will be the origin, and from it will start the referencing
        also, there is a possibility to reference to a specific file by introducing full name of the file
        """
        index = kw_without_input_for_function.index("update_old_chk")
        inp = input_for_function[index]
        if inp[0] == "n-1":
            reference = False
            print("All files will be referencing file n-1")
        else: 
            reference = inp[0]
            if "zero" in reference.lower():
                for file in os.listdir(path_to_folder):
                    if file.endswith(extension):
                        if ((("_X+0" + extension) or "_X+0_") in file) or ((("_Y+0" + extension) or "_Y+0_") in file) or ((("_Z+0" + extension) or "_Z+0_") in file):
                            reference = file
            else: reference = inp[0]      #Case of introducing file name 
        if reference:
            print("Selected file for reference is: " + reference)

        update_oldchk_for_files_in_a_folder(path_to_folder, file_extension=".com", reference_from_input=reference)

    if "basis_set" in kw_without_input_for_function:
        """
        This function will introduce basis set for the files were it is desired and not contradicted by kw
        """
        index = kw_without_input_for_function.index("basis_set")
        inp = input_for_function[index]
        
        if inp == None:
            print("No input for function basis_set")
            print("Please specify the input for the function basis_set")
            print("Syntax: basis_set(option)")
            print("Possible options are: 'origin' or 'all', or a file name")
        basis_set_name = read_block_in_file(path_to_file, "kw_basis_set")
        if basis_set_name == [] or basis_set_name == None or basis_set_name[0] == "":
            print("No basis set name was specified")
            print("Please specify the basis set in the corresponding block")
            return
        if "origin" in inp:                               #This will look to introduce basis set to the file with 0 field
            for file in os.listdir(path_to_folder):
                if file.endswith(extension):
                    if ((("_X+0" + extension) or "_X+0_") in file) or ((("_Y+0" + extension) or "_Y+0_") in file) or ((("_Z+0" + extension) or "_Z+0_") in file):
                        print("Adding basis set to file: " + file)
                        with open(os.path.join(path_to_folder, file), "r") as f:
                            lines = f.readlines()
                        with open(os.path.join(path_to_folder, file), "w") as f:
                            for line in lines:
                                if "#" in line.strip():
                                    if "/gen" in line.strip()[-4:]:             #Adding /gen to the end of first kw line if it has not been introduces 
                                        f.write(line)
                                    else: f.write(line.strip() + "/gen\n")
                                    continue
                                if "ChkBasis" in line.strip():                 #Checking if ChkBasis is already in the file. It we have it we cannot introduce the basis set. It will raise a warning.
                                    with open(log_file, "a") as log:
                                        log.write("!!!WARNING!!!\n")
                                        log.write("ChkBasis already in file: " + file + "\n")
                                f.write(line)
                            f.write("\n".join(basis_set_name))
                            f.write("\n\n")
                        break
        elif "all" in inp:
            for file in os.listdir(path_to_folder):
                if file.endswith(extension):
                    print("Adding basis set to file: " + file)
                    with open(os.path.join(path_to_folder, file), "r") as f:
                        lines = f.readlines()
                    with open(os.path.join(path_to_folder, file), "w") as f:
                        for line in lines:
                            if "#" in line.strip():
                                if "/gen" in line.strip()[-4:]:
                                    f.write(line)
                                else: f.write(line.strip() + "/gen\n")
                                continue
                            if "ChkBasis" in line.strip():
                                with open(log_file, "a") as log:
                                    log.write("!!!WARNING!!!\n")
                                    log.write("ChkBasis already in file: " + file + "\n")
                                    log.writable("File_name: " + file + "\n")
                                    log.write("Basis set was added")
                            f.write(line)
                        f.write("\n".join(basis_set_name))
                        f.write("\n\n")
        else: #This is for the case when we specify the basis set ourselves
            with open(os.path.join(path_to_folder, inp[0]), "r") as f:
                lines = f.readlines()
            with open(os.path.join(path_to_folder, inp[0]), "w") as f:
                for line in lines:
                    if "#" in line.strip():
                        if "/gen" in line.strip()[-4:]:
                            f.write(line)
                        else: f.write(line.strip() + "/gen\n")
                        continue
                    f.write(line)
                f.write("\n".join(basis_set_name))
                f.write("\n\n")
        check_double_lines(path_to_folder)

    if "change_kw" in kw_without_input_for_function:
        """
        This keyword will allow us to make folders with different changed keywords
        """
        index = kw_without_input_for_function.index("change_kw")
        inp = input_for_function[index]
        kw_to_change = inp[0].replace(",", " ").split()[0]      #Kw which we want to change is in the 0th index 
        list_of_new_kw = inp[0].replace(",", " ").split()[1:]   #Kws at index 1: are the ones we want to change to

        for i in keywords:
            if "change_kw" in i:                                #In new input files we want to delete the change_kw keyword to avoid recursion 
                str_to_remove_in_change_kw = i
        if inp == None:
            print("No input for function change_kw")
            print("Please specify the input for the function change_kw")
            print("Syntax: change_kw(file_name, new_kw)")
            return
        path_to_folder_minus_one = "/".join(path_to_folder.split("/")[:-1])   #Folder where we will create new folders
        folder_name = path_to_folder.split("/")[-1]                           #name of the original folder, so that we can modify it for the new inputs
        with open(path_to_file, "r") as file:
            original_file_lines = file.readlines()                            #Saving the lines of the original file to copy them into a new folder, but we will delete change_kw
        for i in list_of_new_kw:                                              #Looping over the new keywords
            new_folder_name = folder_name + "_kw_changed_" + i         
            try:                                                              #Avoiding error if the folder exists
                os.mkdir(os.path.join(path_to_folder_minus_one, new_folder_name))
            except: FileExistsError
            #Name for the new input file
            new_input_file_name_folder_i = os.path.join(path_to_folder_minus_one, new_folder_name, original_file_name[:-4] + "_kw_changed_" + i + original_file_name[-4:])
            with open(new_input_file_name_folder_i, "w") as file:
                #Making a new input file with the changed keyword, and with change_kw deleted to avoid recursion
                for line in original_file_lines:
                    if str_to_remove_in_change_kw in line.strip():
                        line = line.replace(str_to_remove_in_change_kw, "")
                    if kw_to_change in line.strip():
                        line = line.replace(kw_to_change, i)
                    file.write(line)
            check_double_lines(os.path.join(path_to_folder_minus_one, new_folder_name))
            print("Now working in folder: ", os.path.join(path_to_folder_minus_one, new_folder_name))
            read_input_file(new_input_file_name_folder_i)       #Using this function to generate the files in the new folder
            print("\n\n")

    
    if "zip" in kw_without_input_for_function:
        """
        Zip function is similar to change_kw, but it will allow us to change multiple keywords at once
        it will make all possible combination of the keywords we want to change
        Example of the input: zip((cphf(grid=sg1), delete), (sg1, sg2, sg3, sg4), (IOp(9/75=2), IOp(9/75=1)))
        the kw in the position 0 of the inner bracket, is the kw we want to change, and the rest are the options we want to change to
        it will make all posible combination. For the example above, it will make 16 ppossible combiations
        """
        index = kw_without_input_for_function.index("zip")
        inp = input_for_function[index]
        if inp == None:
            print("No input for function zip")
            print("Please specify the input for the function zip")
            print("Syntax: zip((kw1, change1, change2, ...), (kw2, change1, change2, ...), ...)")
        inp = get_inp_text(inp[0])
        original_kw = [x.replace(",", " ").split()[0] for x in inp]     #Getting list of kw-s that we will be changing 
        all_kw = [x.replace(",", " ").split() for x in inp]             #Getting list to what we will change the kw. It will include the original kw.
        for i in keywords:
            if "zip" in i:                                              #Deleting the zip kw from the new input files to avoid recursion
                str_to_remove_in_zip = i                   
                print("This kw will be removed")
                print(str_to_remove_in_zip)
        path_to_folder_minus_one = "/".join(path_to_folder.split("/")[:-1]) #Path to the folder where new folders will be created
        folder_name = path_to_folder.split("/")[-1]                         #Name of the original folder
        for new_comb in product(*all_kw):                                   #Looping over all possible combinations
            with open(path_to_file, "r") as file:
                original_file_lines = file.readlines()
            new_folder_name = folder_name + "_kw_changed_" + "_".join(new_comb)

            name = ""
            not_allowed = "()/"             #Not allowed characters in the folder name
            for char in new_folder_name:    #!!!FOR FUTURE TO CHANGE IT TO A SINGLE LIST COMPREHENSION!!!
                if char in not_allowed:
                    continue
                else: name += char
            new_folder_name = name
            try:
                os.mkdir(os.path.join(path_to_folder_minus_one, new_folder_name))
            except: 
                FileExistsError
            name_from_kw = "_".join(new_comb)
            name_from_kw = "".join([char for char in name_from_kw if char not in "()/"])
            new_input_file_name_folder_i = os.path.join(path_to_folder_minus_one, new_folder_name, original_file_name[:-4] + "_kw_changed_" + name_from_kw + original_file_name[-4:])

            with open(new_input_file_name_folder_i, "w") as file:
                for line in original_file_lines:
                    #Removing the zip kw
                    if str_to_remove_in_zip in line.strip():
                        ind_str = line.find(str_to_remove_in_zip)
                        line = line[:ind_str] + line[ind_str + len(str_to_remove_in_zip):]
                        if line.endswith(" "):
                            line = line[:-1]
                        if line.startswith(" "):
                            line = line[1:]
                        if line.strip() == "":
                            continue  
                    #Changing the kw
                    for i, x in enumerate(original_kw):
                        if x in line.strip():
                            if new_comb[i] == "delete":
                                ind_str = line.find(x)
                                line = line[:ind_str] + line[ind_str + len(x):]
                                if line.endswith(" "):
                                    line = line[:-1]
                                if line.startswith(" "):
                                    line = line[1:]
                                if line.strip() == "":
                                    continue  
                            else: line = line.replace(x, new_comb[i])
                    file.write(line)
            
            check_double_lines(os.path.join(path_to_folder_minus_one, new_folder_name))
            print("Now working in folder: ", os.path.join(path_to_folder_minus_one, new_folder_name))
            read_input_file(new_input_file_name_folder_i)
            print("\n\n")


        
        
        return

    return
                    
#path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Example_how_we_want.txt"
path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/input_test_2_august/M062X_101.txt"
read_input_file(path)

