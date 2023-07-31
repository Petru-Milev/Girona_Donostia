import numpy as np
import os
import re
from functions_for_library import *

def change_kw(path_to_file, keywords):
    with open(path_to_file, "r") as file:
        lines = file.readlines()
    with open(path_to_file, "w") as file:
        introducing_new_kw = False
        gaussian_file_started = True
        count_kw_introduced = 0
        for line in lines:
    
            if "#" in line.strip() and gaussian_file_started:
                introducing_new_kw = True

            if introducing_new_kw:
                if count_kw_introduced == 0:
                    for i, line in enumerate(keywords):
                        file.write(line + "\n" if i != len(keywords) - 1 else line)
                    gaussian_file_started = False
                    count_kw_introduced += 1
                if line.strip() == "":
                    introducing_new_kw = False
                    gaussian_file_started = True
            if gaussian_file_started:
                file.write(line)
    return 

def read_input_file(path_to_file, extension = ".com"):

    def generate_files_e_field_in_one_direction(path_to_file, c1, c2, c3, start, finish, step, type_coordinates, type_space, extension = ".com", lines = "" ,new_kw = False):
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
            field = list(field)
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
                for line in lines:                                     #Writting line of the file
                    file.write(line)
                if field[0] == 0 and field[1] == 0 and field[2] == 0:
                    insert_geom(file_name, path_to_geom)
                    None
                else: 
                    file.write("\n\n" + " ".join([str(x) for x in field]) + "\n\n")
            change_line_in_file(file_name, "%chk", "%chk=" + file_name.split("/")[-1][:-4] + ".chk")
            if new_kw:
                if field[0] == 0 and field[1] == 0 and field[2] == 0:
                    None
                else: 
                    change_kw(file_name, new_kw)
            insert_geom(file_name, path_to_geom)
        
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
                if previous_line == "":
                    f.write("\n")
                else: f.write("\n\n")
    
    def insert_geom(path_to_file, path_to_geom):
        if path_to_geom == None:
            return
        
        with open(path_to_file, "r") as file:
            lines = file.readlines()
        for line in lines:
            if "geom=check" in line:
                path_to_geom = "delete"
                break

        if path_to_geom == "delete":
            with open(path_to_file, "r") as file:
                lines = file.readlines()
            with open(path_to_file, "w") as file:
                for line in lines:
                    if "@" in line.strip():
                        continue
                    file.write(line)
            return
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

    primary_functions = {"gen_e_field_direction": 1, "update_old_chk":3, "basis_set" : 2, "change_kw": 3, "delete": 4}
    path_to_folder = "/".join(path_to_file.split("/")[:-1])
    original_file_name = path_to_file.split("/")[-1]
    with open(path_to_file, "r") as file:
        kw_lines = []
        for i, line in enumerate(file):
            if line.strip() == "":
                line_kw_end = i
                break
            else: kw_lines.append(line.strip())
    keywords = []
    for line in kw_lines:
        keywords.extend(re.split(r'\s(?![^(]*\))',line.strip()))
    keywords = keywords[1:]
    with open(path_to_file, "r") as file:
        original_file_lines = []
        record_file = False
        for line in file:
            if "***start_gaussian_file***" in line.strip().lower():
                record_file = True
                continue
            if record_file:
                original_file_lines.append(line)
    kw_without_input_for_function = []
    input_for_function = []
    for i in keywords:
        kw_without_input_for_function.append(i.split("(")[0])
        input_for_function.append(re.findall(r'\((.*?)\)', i) if re.findall(r'\((.*?)\)', i) else None)

    print("list of keywords: ", kw_without_input_for_function)

    if "read_geom" in kw_without_input_for_function:
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
                        if ("X+0" in file) or ("Y+0" in file) or ("Z+0" in file):
                            reference = file
            else: reference = inp[0]
        if reference:
            print("Selected file for reference is: " + reference)

        update_oldchk_for_files_in_a_folder(path_to_folder, file_extension=".com", reference_from_input=reference)

    if "basis_set" in kw_without_input_for_function:
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
        if "origin" in inp:
            for file in os.listdir(path_to_folder):
                if file.endswith(extension):
                    if ("X+0" in file) or ("Y+0" in file) or ("Z+0" in file):
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
                            f.write(line)
                        f.write("\n".join(basis_set_name))
                        f.write("\n\n")
        else:
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
        index = kw_without_input_for_function.index("change_kw")
        inp = input_for_function[index]
        kw_to_change = inp[0].replace(",", " ").split()[0]
        list_of_new_kw = inp[0].replace(",", " ").split()[1:]

        for i in keywords:
            if "change_kw" in i:
                str_to_remove_in_change_kw = i
        if inp == None:
            print("No input for function change_kw")
            print("Please specify the input for the function change_kw")
            print("Syntax: change_kw(file_name, new_kw)")
        path_to_folder_minus_one = "/".join(path_to_folder.split("/")[:-1])
        folder_name = path_to_folder.split("/")[-1]
        with open(path_to_file, "r") as file:
            original_file_lines = file.readlines()
        for i in list_of_new_kw:
            new_folder_name = folder_name + "_kw_changed_" + i
            try:
                os.mkdir(os.path.join(path_to_folder_minus_one, new_folder_name))
            except: FileExistsError
            new_input_file_name_folder_i = os.path.join(path_to_folder_minus_one, new_folder_name, original_file_name[:-4] + "_kw_changed_" + i + original_file_name[-4:])
            with open(new_input_file_name_folder_i, "w") as file:
                for line in original_file_lines:
                    if str_to_remove_in_change_kw in line.strip():
                        line = line.replace(str_to_remove_in_change_kw, "")
                        print("-----------")
                        print("changed_line")
                        print(line)
                        print("------------")
                    if kw_to_change in line.strip():
                        line = line.replace(kw_to_change, i)
                    file.write(line)
            check_double_lines(os.path.join(path_to_folder_minus_one, new_folder_name))
            print("Now working in folder: ", os.path.join(path_to_folder_minus_one, new_folder_name))
            read_input_file(new_input_file_name_folder_i)
            print("\n\n")
    return
                        







path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Example_how_we_want.txt"



read_input_file(path)