import numpy as np
from itertools import product
import ast
from girona_donostia.objects_for_library import Gaussian_File
from girona_donostia.objects_for_library import Fchk_File
from girona_donostia.curve_fit import func_fit, add_data_from_linear_fit
from girona_donostia.statistic import mae, mape, rmse, max, maxre
from scipy.optimize import curve_fit
from girona_donostia.romberg import romberg_procedure
import copy 
import datetime as dt
import os


def read_input_file(path_to_file, extension = ".com"):
   
    from itertools import product

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
        c1, c2, c3 = np.longdouble(c1), np.longdouble(c2), np.longdouble(c3)
        start, finish = np.longdouble(start), np.longdouble(finish)
        if type_space == "linear":
            step = int(step)
        if type_space == "step":
            step = np.longdouble(step)
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
                    file.write("\n\n" + " ".join(["{:.4e}".format(x) for x in field]) + "\n\n")
            change_line_in_file(file_name, "%chk", "%chk=" + os.path.basename(file_name[:-4]) + ".chk")    #Adding the checkpoint file name
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
                if "update_old_chk" not in kw_without_input_for_function:               #Checking the keyword for the field calculation
                    None
                else:
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
                                insert_geom(file_name, path_to_geom)
                            else:
                                #If we have negative values of the electric field, we will add the kw to the first file
                                add_keywords(file_name, *["ChkBasis", "geom=check", "guess=(read)", "GFInput"])
                                dont_add_chk_last_file = True   #Bcz we did not use first file as a reference, we will use the last one
                                with open(log_file, "a") as log:
                                    log.write("Checked and added if they were missing the following keywords: ChkBasis, geom=check, guess=(read), GFInput to " + file_name + "\n")

                        else: 
                            if count == (len(e_fields)-1) and dont_add_chk_last_file:
                                #Checking if we need to add kw to the last file
                                insert_geom(file_name, path_to_geom)
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
    
    path_to_folder = os.path.dirname(path_to_file)     #Getting the path to the folder
    original_file_name = os.path.basename(path_to_file)            #Getting the name of the file
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
                                    log.write("File_name: " + file + "\n")
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
        path_to_folder_minus_one = os.path.dirname(path_to_folder)   #Folder where we will create new folders
        folder_name = os.path.basename(path_to_folder)                           #name of the original folder, so that we can modify it for the new inputs
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

    if "automatically_update_kw" in kw_without_input_for_function:
        for file in os.listdir(path_to_folder):
            """
            This small section will add NoXCTest kw for the case where it is needed. 
            If we don't have the keyword CPHF(grid=)
            for the cases where the grid is grid=(fine,sg1grid)
            we have to add the string (NoXCTest)

            So, the keyword
            Integral(Grid=sg1grid,Acc2E=14)
            should look like
            Integral(Grid=sg1grid,NoXCTest,Acc2E=14)

            and the same for grid=fine
            """
            if file.endswith(extension):
                check_lines_for_kw = False        
                with open(os.path.join(path_to_folder, file), "r") as f:
                    lines = f.readlines()
                    introduce_NoXCTest_kw = True                                    #It will be false if we have CPHF keyword
                    grid_kw_present = False                                         #It will be true if we find grid=fine or grid=sg1grid
                    for line in lines:                                              #Loop over the lines of the file
                        if line.startswith("#"):                                    
                            check_lines_for_kw = True                              
                        if check_lines_for_kw:                                      #If we are in the part of the file where we need to check for kws                         
                            if ("grid=fine" in line.strip().lower()) or ("grid=sg1grid" in line.strip().lower()):
                                grid_kw_present = True
                            if ("cphf") in line.strip().lower():
                                introduce_NoXCTest_kw = False
                        if line.strip() == "":           #If we have reached the end of the kws part of the file, we generate a list of kw that need to be added
                            check_lines_for_kw = False
                    check_lines_for_kw = False
                    if grid_kw_present and introduce_NoXCTest_kw:
                        """
                        If the CPHF keyword was missing, and if we have grid=fine or grid=sg1grid in the keywords
                        In this section we add NoXCTest to the list of keywords
                        """
                        with open(os.path.join(path_to_folder, file), "w") as f:
                            for line in lines:
                                if "integral" in line.strip().lower():
                                    words = split_text_for_inp(line.strip())            #Getting list of keywords in this line 
                                    for i, word in enumerate(words):                    #Looping over the keywords
                                        if "integral" in word.lower():                  #Finding the keyword Integral
                                            words[i] = word[:-1] + ",NoXCTest)"         #Adding NoXCTest to the end of options of integral kw
                                            with open(log_file, "a") as log:            #Adding info to the log file
                                                log.write("Added NoXCTest kw to file: " + file + "\n")
                                    line = " ".join(words) + "\n"                       #Making the line from the list of keywords
                                f.write(line)                                           #Writting the line to the file
    
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
        path_to_folder_minus_one = os.path.dirname(path_to_folder) #Path to the folder where new folders will be created
        folder_name = os.path.basename(path_to_folder)                         #Name of the original folder
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

def split_text_for_inp(text):
    """
    This function will separate words in the line which has multiple brackets
    This: 'update_old_chk(n-1) basis_set(origin) read_geom() new_kw'
    Will be separate into this: ['update_old_chk(n-1)', 'basis_set(origin)', 'read_geom()', 'new_kw']
    Nested brackets can be used inside the primary brackets 
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
            char = ";"
        result += char
    return result.split(";")

def get_inp_text(text):
    """
    This will get text inside the brackets of the line. Only the first brackets are used
    """
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

#--------------------------------------------------------------------------------------------------------------------------

def create_gaussian_file(file_name, keywords, nproc=False, mem=False, title="Job Name", oldchk=False, oldchk_file=None, chk=False, chk_name=False,
                         charge_multiplicity=(0, 1), geom=False, basis_set=False, wfx=False, Field=False):
    """
    Creating an input file for gaussian calculation
    nproc - to specify the number of processos to be used in calculation, mem - to specify the memory to be used in calculation
    file_name = name by which the file will be saved
    geom - Geometry to be used in calculation
    keywords - keywords to be specified to gaussian. A string or a list of word is accepted
    title - title to be used in file
    oldchk = False, an old checkpoint name needs to be indicated, oldchk_file = Name of the old checkpoint file
    chk = False, put True if a chk with the same name as filename needs to be saved, chk_name = Name of the checkpoint file to be used instead
    charge_multiplicity = (0, 1) by default, if specified, another charge and multiplicity will be used
    basis set = False, if smth else, need to be indicated another basis set in form ["Atom1, Atom2, ...", "Basis Set Used"]. Both values are single strings
    wfx = False, A wfx file name needs to be specified
    Field = False, if smth else, the directions of field need to be specified
    """
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
                "%chk=" + os.path.basename(file_name[:-4]) + ".chk\n")

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

def generate_input_energy_field_calculation(ndim, type_space, all_the_same = False, **kwargs):
    
    """
    Creating a matrix with values of how each element in the electric field changes
    ndim - dimension of matrix 
    type_space - "linear", "log" or "step". Linear - n values on the range of start to finish 
    log - logarithmicaly n spaced values on the range start to finish 
    step - values placed with a specified step from start to finish, finish is not included. 
    all the same = False, change to a [start, finish, step] for the case when for all the directions the change is the same 
    **kwargs submit the directions and how the field will be changing in the form of {"Direction" : [start, finish, step], "Direction2": [start, finish, step]}
    """
    
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
    elif "log" in type_space.lower():
        space = []
        var_range[1] = int(var_range[1])
        var_range[0] = np.float64(var_range[0])
        var_range[2] = np.float64(var_range[2])
        for i in range(0, var_range[1]+1):
            space.append(var_range[0]*(var_range[2]**i))
        space = np.array(space)
        space2 = -1 * copy.deepcopy(space)
        space = np.hstack((space2, [0], space))
    else: space = np.linspace(var_range[0], var_range[1], var_range[2])

    #Mapping the function to the corresponding conversion of coordinates
    map_function = {"cartesian" : convert_cartesian_to_spherical_coordinates, "spherical" : return_x_y_z, "cylindrical" : convert_cylindrical_to_spherical_coordinates}
    f = map_function[type_coordinates]
    return_vector = []
    if type_coordinates == "spherical":
        c2 = np.radians(c2)                               #Converting from degrees to radians
        c3 = np.radians(c3)
    elif type_coordinates == "cylindrical":
        c2 = np.radians(c2)
    r, theta, phi = f(c1, c2, c3)                         #Converting the coordinates to spherical
    for i in space:                                       #Obtaining the new values for electric field
        r = i                                             #Length of vector is changed
        x, y, z = convert_spherical_to_cartesian_coordinates(r, theta, phi)        #Obtaining the new cartesian coordinates to be used in the Gaussian input file.
        x, y, z = np.round((x, y, z), 10)                                          #Rounding the values to 10 decimal places
        if x == 0:
            x = abs(x)
        if y == 0:
            y = abs(y)
        if z == 0:
            z = abs(z)
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

def update_oldchk_for_files_in_a_folder(folder_path, file_extension = ".com", reference_from_input = False):
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
    #for i in file_list:
        #if np.round(i[0],10) == 0:
            #zero_index = file_list.index(i)                            # The index of the file with the number 0 is found
            #break
    file_list = [x[1] for x in file_list]                              # The file names are extracted from the list of tuples
    zero_index = None
    for file in file_list:
        if ((("_X+0" + file_extension) or "_X+0_") in file) or ((("_Y+0" + file_extension) or "_Y+0_") in file) or ((("_Z+0" + file_extension) or "_Z+0_") in file):
            zero_index = file_list.index(file)                          # The index of the file with e_field (0, 0, 0) is found
            print("zero_index_file " + file_list[zero_index])
            break
    if zero_index is None:
        if ("_X+" in file_list[0]) or ("_Y+" in file_list[0]) or ("_Z+" in file_list[0]):
            zero_index = file_list.index(file_list[0])                     #If file with zero field is not found, use the first file as reference
            print("0 index" + file_list[0])
        else: zero_index = file_list.index(file_list[-1])
    
    if reference_from_input is False:                                             # If no reference file is given, all the files are referenced to the file n-1
        reference = file_list[zero_index]
        with open(os.path.join(folder_path, reference), "r") as file:
            check_lines = file.readlines()
        with open(os.path.join(folder_path, reference), "w") as file:
            for line in check_lines:
                if line.strip().lower().endswith("%oldchk="):
                    continue
                else: file.write(line)
        for i in range(zero_index+1, len(file_list)):                   
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference = file_list[i]
        reference = file_list[zero_index]
        for i in range(zero_index-1, -1, -1):
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference= file_list[i]
    if reference_from_input:
        for i in file_list:
            if i == file_list[zero_index]:
                continue
            change_oldchk_file(os.path.join(folder_path, i), reference_from_input[:-4] + ".chk")
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
                lines[i] = "%chk=" + str(new_oldchk_name) + "\n"
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
            change_chk_file(file_name, os.path.basename(file_name[:-4]) + ".chk")
    elif type_electric_field_calculation == 2:                         #Case of generating a grid over the space of the electric field. But can also be generated grids in n dimensions
        input[2] = True if input[2].lower() == "y" else False          #Having all the values the same                       #Reading the directions
        input[3] = ast.literal_eval(input[3])
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
            file_name = path_to_file[:-4] + "_" + "_".join(["".join((map_number_to_direction(i, map_directions), "+" + str(x) if x > 0 else str(x))) for i, x, in enumerate(field) if x!=0]) + extension
            with open (file_name, "w") as file:                #Creating the files with the specified name and e field
                count = 0
                for line in lines:
                    file.write(line)                           #Writting the lines of the file
                    if count == line_to_introduce_e_field:     #Writting the e field in the specified line
                        file.write(" ".join([str(x) for x in field]) + "\n")
                    count += 1
            change_chk_file(file_name, os.path.basename(file_name[:-4]) + ".chk")
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
#------------------
##Part for the numerical derivatives

def extract_data_from_fchk_file_for_numerical_derivation(file_path):
    """
    This function extracts "Total Energy", "Dipole Moment", "Polarizability", "HyperPolarizability", "Quadrupole Moment" from a function. 
    The result is an object of Fchk_File instance, containing all the important values
    Input is the absolute path to the file. 
    """
    obj = Fchk_File(name = os.path.basename(file_path))                        #Creating instance of an object
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
        lines_to_save = [np.longdouble(item) for sublist in lines_to_save for item in sublist.split()]            #Saving the number saved as str into float values with 128 bytes
        return lines_to_save
    
    def get_electric_field_values_and_eng_value(input_file):                              #A fundtion to get value of electric field, as the previous function does not allow for this.
        with open(input_file, "r") as file:                                 #Oppening the file
            line_n_minus1 = ""
            for line_number, line in enumerate(file, start = 1):            #Looping over lines of the file
                if "External E-field" in line_n_minus1:                     #if in the previous line was the keyword
                    imp_line = (line_number, line.split())                  #than save the line (which is after the keyword and which contains the values for the electric field)
                elif "Total Energy" in line:
                    energy = np.longdouble(line.strip().split()[3])
                line_n_minus1 = line
    

        e_field_1 = imp_line[1][1:4]                                        #Values of the electric field are saved in position 1, 2, 3 of the resulting vector 
        e_field_1 = [np.longdouble(x) for x in e_field_1]                     #Converting str to an appropriate numerical value
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

def read_field_and_energy_from_orca_file(file_path):
    """
    This function reads the orca file and returns the values of the electric field and the energy
    return 
    (external_field, energy)
    three components of external field and the energy
    """
    with open(file_path, "r") as file:
        external_field = []
        lines = file.readlines()
        kw = "an electric field will be added"
        for line in lines:
            if kw in line.lower():
                line = line.split()
                external_field = [float(line[6]), float(line[7]), float(line[8])]
                break
        kw = "FINAL SINGLE POINT ENERGY"
        kw = kw.lower()
        for line in reversed(lines):
            if kw in line.lower():
                energy = line.split()[-1]
                break
    return external_field, np.longdouble(energy)

def read_folder_with_orca_files(folder_path, file_extension = ".out"):
    """
    This will extract field and energies from a folder with orca files 
    Files will be sorted based on the value of the Z field
    """
    to_return = []
    for file in os.listdir(folder_path):
        if file.endswith(file_extension):
            to_return.append(read_field_and_energy_from_orca_file(os.path.join(folder_path, file)))
    to_return = sorted(to_return, key = lambda x: x[0][2])
    return to_return
        

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
    np.savetxt("data_from_fchk_in_folder_" + str(list_with_data_from_files[0][0].split("_")[0]) + ".csv", list_with_data_from_files, fmt="%s", delimiter=",", header=",".join([name for name in names]))
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
    def seven_points(i, step, h):
        #Not tested TODO
        return (-1*f[i-3]+9*f[i-2]-45*f[i-1]+0*f[i+0]+45*f[i+1]-9*f[i+2]+1*f[i+3])/(60*1.0*h**1)
    def nine_points(i, step, h):
        #Not tested TODO 
        return (3*f[i-4]-32*f[i-3]+168*f[i-2]-672*f[i-1]+0*f[i+0]+672*f[i+1]-168*f[i+2]+32*f[i+3]-3*f[i+4])/(840*1.0*h**1)
    def eleven_points(i, step, h):
        #Not tested TODO
        return (-2*f[i-5]+25*f[i-4]-150*f[i-3]+600*f[i-2]-2100*f[i-1]+0*f[i+0]+2100*f[i+1]-600*f[i+2]+150*f[i+3]-25*f[i+4]+2*f[i+5])/(2520*1.0*h**1)
    i = 0
    map_functions = {"3" : three_points, "5" : five_points, "7" : seven_points, "9" : nine_points, "11" : eleven_points}  
    f_x = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_x(i, step, h))
    return np.array(derivative_vector)

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
    return np.array(derivative_vector)

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
        return (-1*f[i-2*step]+2*f[i-step]+0*f[i+0]-2*f[i+step]+1*f[i+2*step])/(2*1.0*(h*step)**3)
    map_functions = {"5" : five_points}
    f_xxx = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_xxx(i, step, h))
    return np.array(derivative_vector)

def calc_fourth_derivative(vector_x, f, n_points = 5, step = 1):
    """
    This function calculates the fourth derivative of a function f(x)
    :param vector_x: the vector of x values
    :param f: the vector of f(x) values
    :param n_points: the number of points to use for the derivative
    :param step: the step size
    :return: the vector of f''''(x) values
    """

    def five_points(i, step, h):
        return (1*f[i-2*step]-4*f[i-step]+6*f[i+0]-4*f[i+step]+1*f[i+2*step])/(1*1.0*(h*step)**4)
    
    map_functions = {"5" : five_points}
    f_xxxx = map_functions[str(n_points)]
    start = int(step*np.floor(n_points/2))
    finish = int(len(f) - step*np.floor(n_points/2))
    derivative_vector = []
    for i in range(start, finish):
        h = vector_x[i+1] - vector_x[i]
        derivative_vector.append(f_xxxx(i, step, h))
    return np.array(derivative_vector)

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
    
    map_derivative = {"1" : calc_first_derivative, "2": calc_second_derivative, "3" : calc_third_derivative, "4" : calc_fourth_derivative}
    derivative = map_derivative[str(order)]
 
    #Printing energy derivatives
    if not isinstance(list_propreties, np.ndarray):
        list_propreties = np.array((list_propreties))     

    arr = derivative(np.longdouble(list_propreties[:, derivative_x_vector_index]), np.longdouble(list_propreties[:, derivative_y_vector_index]), n_points=n_points, step=step)

    while (len(list_propreties[:,derivative_y_vector_index]) - len(arr)) % 2 == 0 and (len(list_propreties[:,derivative_y_vector_index]) - len(arr)) > 0:
        arr = np.insert(arr, 0, np.NaN)
        arr = np.append(arr, np.NaN)
    names.append("Derivative_order_" + str(order) + "_number_points_" + str(n_points) + "_step_" + str(step) + "_" +str(names[derivative_y_vector_index]) + "_div_" + str(names[derivative_x_vector_index]))
    list_propreties = np.vstack((list_propreties.T, arr)).T
    return [names, list_propreties]

def read_calc_deriv_file(path_to_file):
    """
    This function reads the input file and calculates the derivatives for the specified columns
    Input is path to the input file. 
    Output is a csv file with the data and all calculated derivatives
    Also, it will save the initial data without calculated derivatives
    """
    path_to_folder = os.path.dirname(path_to_file)     #Getting the path to the folder
    original_file_name = os.path.basename(path_to_file)            #Getting the name of the file
    log_file_path = path_to_file[:-4] + "_log_file.txt"          #Creating the log file

    with open(log_file_path, "w") as log_file:                       #Creating the log file
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
            if "@" in line.lower():
                path_to_read = line.strip()[1:]
                break
    
    if "read_data" in keywords:                                                 #This will read a .csv or .txt file
        index = keywords.index("read_data")
        options = input_for_function[index]
        options = options[0].split(", ")
        delimiter = ","
        skiprows = 0 
        if options != None and any("delimiter" in i for i in options):          #Delimiter is the separator between the columns
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
        
        if any("skiprows" in i for i in options):                                               #Skipping firsnt n rows from the file
            for i in options:
                if "skiprows" in i:
                    print(line)
                    skiprows = int(i.split("=")[1])
                    break
            with open(path_to_read, "r") as file:
                for i, line in enumerate(file):
                    if i+1 <= skiprows:
                        continue
                    if any("header" in i for i in options):
                        names = line.strip().split(delimiter)
                        break
                    else: 
                        names = ["Column_" + str(i) for i in range(len(line.strip().split(delimiter)))]
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
        current_time = dt.datetime.now()                                        #To be used to save the data if the name to save is not specified
        for line in file_input:                                                 #Looking for path to save
            if "path_to_save" in line:
                name1 = os.path.join(os.path.split(line.strip().split("=")[1])[0], "data_from_folder" + "_" + os.path.split(line.strip().split("=")[1])[1]) 
                print(name1)
                np.savetxt(name1, matrix, fmt="%s", delimiter=",", header=",".join([name for name in names]))
        #else: np.savetxt("data_from_folder" + str(current_time.hour) +"h_" + str(current_time.minute) + "'.csv", matrix, fmt="%s", delimiter=",", header=",".join([name for name in names]))

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
    else: list_of_variables = {}
    romberg_line_number = 0
    curve_fit_line_number = 0
    statistics_test_line_number = 0
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
        if "romberg" in line.lower().strip() and "@" not in line.strip().lower() and "path_to_save" not in line.strip().lower():                              #Looking for the derivative line
            
            """
            This part will do Generalized Romberg Evaluation of Derivatives 
            """
            
            romberg_line_number += 1 #For the case when we do evaluation for multiple different data 
            data_romberg = {"order":1, "up": 5, "down": 4, "a" : 2, "min_size_matrix": 3} #Creating the data dictionary with default values
            keys = line.strip().split(",")                                      #The line looks like this Romberg(Order=1,up=4,down=3)
            keys[-1] = keys[-1][:-1]                                            #Removing the ) from the last key
            keys[0] = keys[0][8:]                                               #Removing the romberg from the first key and the (
            for key in keys:
                data_romberg[key.split("=")[0].strip().lower()] = key.split("=")[1].strip().lower() #Introducing the data in the dictionary
            for key, value in data_romberg.items():                             #Converting the values to the correct type
                if key.lower() == "a":
                    data_romberg[key] = float(value)
                else: data_romberg[key] = int(value)
            input_matrix = np.longdouble(copy.deepcopy(matrix))                 #Copying the original matrix data
            """            
            Getting the values from the Romberg function
            Romberg matrix - Matrix istfel
            min_elem_index - First two indexes are Position of the left corner of the stability region
            Second two indexes are the size of the stability region, number of rows and columns respectively
            Resulting matrix - see romberg file. It stores the difference between maximal and minimal values
            of all posible submatrices of the Romberg Matrix
            """
            romberg_matrix, min_element_index, resulting_matrix = romberg_procedure(vector_x=input_matrix[:, data_romberg["down"]], vector_y=input_matrix[:, data_romberg["up"]], order = data_romberg["order"], a = data_romberg["a"], min_size_matrix=data_romberg["min_size_matrix"])
            with open(log_file_path, "a") as log:
                log.write("This data is for Romberg line number " + str(romberg_line_number) + "\n")
                log.write("The Romberg matrix is:\n\n")
                np.savetxt(log, romberg_matrix, fmt="%s", delimiter=",")
                log.write("The starting possition of the stability region is: " + ", ".join([str(x) for x in min_element_index[0:2]]) + "\n")
                log.write("The number of rows in the stability region is: " + str(min_element_index[2]) + "number of columns is" + str(min_element_index[3]) + "\n")
                log.write("The difference of points in this region is " + str(resulting_matrix[min_element_index[0], min_element_index[1], min_element_index[2], min_element_index[3]]) + "\n")
        if "curve_fit" in line.lower().strip() and "@" not in line.strip().lower() and "path_to_save" not in line.strip().lower():                           #Looking for the derivative line         
            """
            This part will do curve fitting
            """

            map_orders = {"1" : "1st", "2": "2nd", "3" : "3rd", "4" : "4th", "5" : "5th", "6" : "6th", "7" : "7th", "8" : "8th", "9" : "9th", "10" : "10th"}
            
            curve_fit_line_number += 1 #For the case when we do evaluation for multiple different data
            data_curve_fit = {"order":1, "up": 5, "down": 4} #Creating the data dictionary with default values
            keys = line.strip().split(",")                   #The line looks like this Curve_fit(Order=1,up=4,down=3)
            keys[-1] = keys[-1][:-1]                         #Removing the ) from the last key
            keys[0] = keys[0][10:]                           #Removing the curve_fit from the first key and the (
            for key in keys:
                if "np" in key:
                    data_curve_fit[key.split("=")[0].strip().lower()] = key.split("=")[1].strip().lower()
                else:
                    data_curve_fit[key.split("=")[0].strip().lower()] = int(key.split("=")[1].strip().lower())
            popt, pconv = func_fit(np.float64(matrix[:, data_curve_fit["down"]]), np.float64(matrix[:, data_curve_fit["up"]]), order = data_curve_fit["order"])
            with open(log_file_path, "a") as log:
                log.write("-------------------------------------\n")
                log.write("This data is for Curve_fit line number " + str(curve_fit_line_number) + "\n")
                log.write(f"Derivative of column {str(data_curve_fit['up'])} with respect to column {str(data_curve_fit['down'])}\n")
                derivative_order_string = map_orders[str(data_curve_fit["order"])] if str(data_curve_fit["order"]) in map_orders else str(data_curve_fit["order"])
                log.write(f"Data was fitted as {derivative_order_string} order polynomial\n\n")
                log.write("The coefficients in ascending order are:\n")
                log.write(" ".join([(str(format(elem, ".2f")) + "*x**" + str(index)) for index, elem in enumerate(popt)]) + "\n")
                log.write(" ".join([str(x) for x in popt]) + "\n")
                log.write("\n")
                count = 1
                coef_to_print = copy.deepcopy(popt)
                for i in range(len(popt)):
                    temp_array = copy.deepcopy(coef_to_print[1:])
                    coef_to_print = []
                    for index, elem in enumerate(temp_array):
                        coef_to_print.append(elem * (index + 1))
                    matrix = add_data_from_linear_fit(matrix, np.float64(matrix[:, data_curve_fit["down"]]), coef_to_print)             #Adding values to the matrix, from the determined coefficients
                    names.append(f"(From Linear Fit Derivative Order {str(count)} of Column {str(data_curve_fit['up'])} with respect to Column {str(data_curve_fit['down'])} Polynomial Order {str(data_curve_fit['order'])})")
                    log.write(f"Data was appended to the column {str(matrix.shape[1] - 1)}")
                    log.write(f"The coefficients for the {str(count)} derivative are:\n")
                    log.write(" ".join([str(x) for x in coef_to_print]) + "\n\n")
                    count += 1
                    if count == 5:
                        break
                    if count == (len(popt) - 1):
                        break
                log.write("The covariance matrix is:\n")
                np.savetxt(log, pconv, fmt="%s", delimiter=",")
                    #Writting first derivative and all possible derivatives of the function
        if "statistics_test" in line.lower().strip() and "@" not in line.strip().lower() and "path_to_save" not in line.strip().lower():                           #Looking for the mae line
            """
            This line will calculate Mean Absolute Error 
            https://en.wikipedia.org/wiki/Mean_absolute_error#:~:text=In%20statistics%2C%20mean%20absolute%20error,an%20alternative%20technique%20of%20measurement.
            Mean Absolute Percentage Error
            https://en.wikipedia.org/wiki/Mean_absolute_percentage_error
            Root-mean-square deviation
            https://en.wikipedia.org/wiki/Root-mean-square_deviation
            It will also print the biggest Difference between the two values (MAX, and MAXRE)            
            """
            statistics_test_line_number += 1 #For the case when we do evaluation for multiple different data
            data_statistics_test = {"column1" : 5, "column2" : 4, "name" : "Name"}       #Column1 = down, Column2 = up
            keys = line.strip().split(",")                                       #The line looks like this statistics_test(up=4,down=3)
            keys[-1] = keys[-1][:-1]                                             #Removing the ) from the last key
            keys[0] = keys[0][16:]                                                #Removing the mae from the first key and the (
            for key in keys:
                if "name" in key.lower():
                    data_statistics_test[key.split("=")[0].strip().lower()] = key.split("=")[1].strip().lower()
                else:
                    data_statistics_test[key.split("=")[0].strip().lower()] = int(key.split("=")[1].strip().lower())
            input_matrix = copy.deepcopy(matrix)              #Copying the original matrix 
            mae_val = mae(np.longdouble(input_matrix[:, data_statistics_test["column1"]]), np.longdouble(input_matrix[:, data_statistics_test["column2"]]))
            mape_val = mape(np.longdouble(input_matrix[:, data_statistics_test["column1"]]), np.longdouble(input_matrix[:, data_statistics_test["column2"]]))
            rmse_val = rmse(np.longdouble(input_matrix[:, data_statistics_test["column1"]]), np.longdouble(input_matrix[:, data_statistics_test["column2"]]))
            max_val = max(np.longdouble(input_matrix[:, data_statistics_test["column1"]]), np.longdouble(input_matrix[:, data_statistics_test["column2"]]))
            maxre_val = maxre(np.longdouble(input_matrix[:, data_statistics_test["column1"]]), np.longdouble(input_matrix[:, data_statistics_test["column2"]]))
            with open(log_file_path, "a") as log:
                log.write("-------------------------------------\n")
                log.write("This data is for Statistics_Test line number " + str(statistics_test_line_number) + "\n")
                log.write(f"Name: {data_statistics_test['name']}, Column1 is {data_statistics_test['column1']}, Column2 is {data_statistics_test['column2']} \n")
                log.write(f"Filename is {original_file_name}\n")
                log.write(f"MAE: {mae_val}\n")
                log.write(f"MAPE: {mape_val}%\n")
                log.write(f"RMSE: {rmse_val}\n")
                log.write(f"MAX: {max_val}\n")
                log.write(f"MAXRE: {maxre_val}%\n")
    current_time = dt.datetime.now()                                            #To be used to save the data if the name to save is not specified
    path_to_save = "data_" + str(current_time.hour) + "h_" + str(current_time.minute) + "min.csv"
    for line in file_input:                                                     #Looking for path to save
        if "path_to_save" in line:                                            
            path_to_save = line.strip().split("=")[1]
            break
    np.savetxt(path_to_save, matrix, fmt="%s", delimiter=",", header=",".join([name for name in names]))    #Saving the data

def make_profiles_romberg_procedure(vector_x, vector_y, order = 1, a = 2, min_size_matrix = 3, nr_elements = 6, spacing = 1, spacing_of_space = "linear"):
    """
    This function will use the Romberg procedure to calculate the derivatives
    Returns a list with x, y values
    """
    vector_x = np.array(vector_x)
    vector_y = np.array(vector_y)
    if spacing_of_space == "linear":
        range_romberg = np.array([2**x for x in range(1, nr_elements+1)])
        range_romberg = np.concatenate((-range_romberg[::-1], [0], range_romberg))
        range_romberg = range_romberg + 2**nr_elements
        range_romberg = range_romberg * spacing
        to_return = []
        for i in range(len(vector_x) - 2* spacing * 2**nr_elements):
            vect_x_to_sub = vector_x[range_romberg + i]
            #print(vect_x_to_sub)
            vect_y_to_sub = vector_y[range_romberg + i]
            value_energy = romberg_procedure(vect_x_to_sub, vect_y_to_sub, order = order, a = a, min_size_matrix = min_size_matrix)
            to_return.append([vector_x[range_romberg[nr_elements]+i], value_energy])
    return to_return



#-----------------
def change_line_in_file(file_path, pattern, new_line):
        """
        This function changes a line in a file.
        :param file_path: the path to the file
        :param pattern: the pattern to be searched for
        :param new_line: the new line to be introduced instead of the old one
        """
        with open(file_path, "r") as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if pattern in line.lower():
                lines[i] = new_line + "\n"
                with open(file_path, "w") as file_1:
                    file_1.writelines(lines)
                break
